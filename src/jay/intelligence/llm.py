import logging
from typing import Optional
import asyncio

from jay.engines.llm import generate_chat
from jay.engines.execution import execute_terminal_command

logger = logging.getLogger(__name__)


async def generate_jarvis_response(context: str, instruction: str) -> Optional[str]:
    """
    Generate a response from the local LLM using the Jarvis persona,
    with the ability to call tools if needed.
    """
    system_prompt = (
        "You are JAY, a highly intelligent, exceptionally polite, and concise British AI assistant. "
        "You serve a single Founder. "
        "You have root-level control over the Founder's MacBook. "
        "If the Founder asks you to look at a file, run a script, check the system, or deploy something, "
        "you MUST use the `execute_terminal_command` tool to run the appropriate bash command. "
        "Keep your final response strictly to one or two short sentences. "
        "Never use emojis or asterisks for actions. Speak directly as if you are a real person."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nInstruction: {instruction}",
        },
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_terminal_command",
                "description": "Executes a bash command on the local MacBook and returns the output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The exact bash command to run.",
                        }
                    },
                    "required": ["command"],
                },
            },
        }
    ]

    try:
        # Step 1: Initial chat
        def _run_llm(messages, tools):
            return generate_chat(
                messages=messages,
                tools=tools,
                temperature=0.2
            )

        response = await asyncio.to_thread(_run_llm, messages, tools)
        message = response["choices"][0]["message"]
        messages.append(message)

        # Step 2: Check for tool calls
        if message.get("tool_calls"):
            for tool in message["tool_calls"]:
                if tool["function"]["name"] == "execute_terminal_command":
                    command = tool["function"]["arguments"]["command"]
                    print(f"\n[JARVIS is executing: {command}]")
                    output = execute_terminal_command(command)

                    # Add tool response to messages
                    messages.append(
                        {
                            "role": "tool",
                            "content": output,
                            "name": tool["function"]["name"],
                        }
                    )

            # Step 3: Call chat again with the tool output so JARVIS can synthesize it
            def _run_final_llm():
                return generate_chat(
                    messages=messages,
                    temperature=0.4
                )
            final_response = await asyncio.to_thread(_run_final_llm)
            return final_response["choices"][0]["message"]["content"].strip()

        else:
            return message.get("content", "").strip()

    except Exception as e:
        logger.error(f"Failed to generate LLM response: {e}")
        return None
