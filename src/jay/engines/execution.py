import logging

from jay.db import SessionLocal

logger = logging.getLogger(__name__)

from jay.tools.registry import registry
from jay.engines.trust import ExecutionPolicyEngine, PolicyVerdict, RealityCheckEngine


class ExecutionEngine:
    def __init__(self):
        pass

    async def delegate_task(self, task_description: str) -> str:
        import asyncio
        import json
        from jay.engines.llm import generate_chat
        
        import os
        constitution_text = ""
        docs_path = os.path.join(os.path.dirname(__file__), "../../../docs/JAY_WEBSITE_CONSTITUTION.md")
        if os.path.exists(docs_path):
            with open(docs_path, "r") as f:
                constitution_text = f.read()

        system_prompt = (
            "You are an autonomous sub-agent of JAY. You have access to a secure Tool Registry.\n"
            "Your entire output MUST be a strict JSON object matching the AgentAction schema.\n"
            "To execute a function, set action to 'tool', and provide 'tool_name' and 'tool_arguments'.\n"
            "If the task is fully complete, set action to 'done' and provide the 'result'.\n"
            "Wait for the OBSERVATION. Based on the output, decide your next move.\n"
            "AVAILABLE TOOLS:\n"
            "1. read_file (args: path) - Read a file.\n"
            "2. write_file (args: path, content) - Write to a file.\n"
            "3. search_files (args: directory, pattern) - Find files.\n"
            "4. git_status (args: {}) - Check git status.\n"
            "CRITICAL RULES:\n"
            "1. ONLY output JSON. NO other text or markdown block formatting.\n"
            "2. If a tool requires human approval, you will receive 'Command queued for Founder approval'. You must then output 'action': 'wait_approval' to gracefully pause your execution.\n\n"
            "WEBSITE CONSTITUTION (FOR UI/FRONTEND TASKS ONLY):\n"
            f"{constitution_text}\n"
            "If building UI, you MUST format it as a premium Silicon Valley product (Linear, Apple, Stripe) or you will fail the review board."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"TASK: {task_description}"}
        ]
        
        from jay.engines.schemas import AgentAction
        
        # Build state machine ledger entry
        import uuid
        from jay.engines.models import ExecutionWorkflowLedger
        
        workflow_id = str(uuid.uuid4())
        with SessionLocal() as db:
            workflow = ExecutionWorkflowLedger(id=workflow_id, agent_id="subagent", state="PLANNING", context=task_description)
            db.add(workflow)
            db.commit()

        max_loops = 10
        for loop_idx in range(max_loops):
            def _run_llm():
                return generate_chat(
                    messages=messages,
                    temperature=0.1,
                    response_format={
                        "type": "json_object",
                        "schema": AgentAction.model_json_schema()
                    }
                )
            
            try:
                response = await asyncio.to_thread(_run_llm)
                content = response["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.error(f"Agent LLM error: {e}")
                with SessionLocal() as db:
                    w = db.query(ExecutionWorkflowLedger).filter_by(id=workflow_id).first()
                    w.state = "FAILED"
                    w.last_result = str(e)
                    db.commit()
                return f"Error executing local model: {e}"
                
            messages.append({"role": "assistant", "content": content})
            logger.info(f"[Agent Loop {loop_idx}] LLM generated structured JSON: {content}")
            
            # Pydantic parsing - ZERO REGEX
            try:
                data = json.loads(content)
                action_obj = AgentAction(**data)
            except Exception as e:
                logger.error(f"Failed to parse Pydantic schema: {e}")
                messages.append({"role": "user", "content": f"Error: Invalid JSON or Schema violation: {e}. Retry."})
                continue
                
            with SessionLocal() as db:
                w = db.query(ExecutionWorkflowLedger).filter_by(id=workflow_id).first()
                w.state = "EXECUTING" if action_obj.action == "tool" else "VERIFYING"
                db.commit()

            if action_obj.action == "done":
                # Phase 9.7: Reality Engine Check
                if not RealityCheckEngine.verify_completion(task_description, action_obj.result):
                    logger.warning("Reality Check Failed for task completion.")
                    messages.append({
                        "role": "user", 
                        "content": "Error: Reality Check Failed. You marked the task as done, but provided insufficient physical evidence (e.g. URLs, commit hashes, or detailed proof). Retry with proof or use tools to verify."
                    })
                    continue
                
                with SessionLocal() as db:
                    w = db.query(ExecutionWorkflowLedger).filter_by(id=workflow_id).first()
                    w.state = "COMPLETED"
                    w.last_result = action_obj.result
                    db.commit()
                return action_obj.result or "Task marked as done and verified by Reality Engine."
            
            elif action_obj.action == "wait_approval":
                with SessionLocal() as db:
                    w = db.query(ExecutionWorkflowLedger).filter_by(id=workflow_id).first()
                    w.state = "WAITING_APPROVAL"
                    db.commit()
                return "Execution paused. Waiting for Founder approval."
            
            elif action_obj.action == "tool":
                tool_name = action_obj.tool_name
                arguments = action_obj.tool_arguments or {}
                if not tool_name:
                    messages.append({"role": "user", "content": "Error: No tool_name provided."})
                    continue
                
                logger.info(f"[Agent Loop] Attempting tool '{tool_name}' with args {arguments} (Confidence: {action_obj.confidence})")
                
                manifest = registry.get_manifest(tool_name)
                if not manifest:
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' does not exist in registry."})
                    continue
                    
                verdict = ExecutionPolicyEngine.evaluate(manifest, arguments)
                logger.info(f"[Trust Gate] Verdict for {tool_name}: {verdict.value}")
                
                if verdict == PolicyVerdict.BLOCKED:
                    observation = f"Error: Tool '{tool_name}' execution was BLOCKED by JAY Trust Gate due to severe risk."
                elif verdict == PolicyVerdict.FOUNDER_APPROVAL:
                    with SessionLocal() as db:
                        w = db.query(ExecutionWorkflowLedger).filter_by(id=workflow_id).first()
                        w.state = "WAITING_APPROVAL"
                        w.context = f"Tool: {tool_name}, Args: {arguments}"
                        db.commit()
                    observation = "Command queued for Founder approval. Execution paused."
                else:
                    observation = registry.execute(tool_name, arguments)
                
                logger.info(f"[Agent Loop] Observation: {observation}")
                messages.append({"role": "user", "content": f"OBSERVATION: {observation}"})
            else:
                messages.append({"role": "user", "content": "Error: Unknown action."})
                
        with SessionLocal() as db:
            w = db.query(ExecutionWorkflowLedger).filter_by(id=workflow_id).first()
            w.state = "FAILED"
            w.last_result = "Exceeded maximum loops"
            db.commit()
        return "Error: Subagent exceeded maximum loop count."
