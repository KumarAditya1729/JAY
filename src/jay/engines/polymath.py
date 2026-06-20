from sqlalchemy.orm import Session
from jay.engines.models import ExpertFrameworkLedger
from jay.chief_of_staff.schemas import ExpertAdvice
from jay.config import get_settings
from jay.engines.llm import generate_chat


class PolymathEngine:
    def __init__(self, session: Session):
        self.session = session
        self.ensure_seed_data()

    def ensure_seed_data(self):
        count = self.session.query(ExpertFrameworkLedger).count()
        if count == 0:
            seed_data = [
                {
                    "expert_name": "Jeff Bezos",
                    "framework_name": "Regret Minimization Framework",
                    "core_principle": "Project yourself forward to age 80 and look back. Make the decision that minimizes the number of regrets you will have.",
                    "application_criteria": "When facing high-risk, high-reward career or strategic decisions.",
                },
                {
                    "expert_name": "Charlie Munger",
                    "framework_name": "Inversion Principle",
                    "core_principle": "Instead of trying to figure out how to succeed, figure out how to fail, and then avoid doing those things.",
                    "application_criteria": "When planning projects, assessing risks, or solving complex problems.",
                },
                {
                    "expert_name": "Elon Musk",
                    "framework_name": "First Principles Thinking",
                    "core_principle": "Boil things down to the most fundamental truths and then reason up from there, rather than reasoning by analogy.",
                    "application_criteria": "When innovating, designing architecture, or solving engineering bottlenecks.",
                },
                {
                    "expert_name": "Naval Ravikant",
                    "framework_name": "Leverage and Judgment",
                    "core_principle": "Fortunes require leverage. Business leverage comes from capital, people, and products with no marginal cost of replication (code and media). Use judgment to direct leverage.",
                    "application_criteria": "When prioritizing tasks, delegating, or deciding what projects to pursue.",
                },
            ]
            for f in seed_data:
                self.add_expert_framework(
                    f["expert_name"], f["framework_name"], f["core_principle"], f["application_criteria"]
                )
                
    def add_expert_framework(self, expert_name: str, framework_name: str, core_principle: str, application_criteria: str):
        record = ExpertFrameworkLedger(
            expert_name=expert_name,
            framework_name=framework_name,
            core_principle=core_principle,
            application_criteria=application_criteria,
        )
        self.session.add(record)
        self.session.commit()

    async def apply_framework(
        self, statement: str, context: str
    ) -> ExpertAdvice | None:
        frameworks = self.session.query(ExpertFrameworkLedger).all()
        if not frameworks:
            return None

        # In a real system, we might use embeddings to find the best framework.
        # For Phase 6.7, we'll let the LLM choose the best framework and apply it.

        fw_text = "AVAILABLE MENTAL MODELS:\n"
        for i, f in enumerate(frameworks):
            fw_text += f"{i+1}. {f.expert_name} - {f.framework_name}: {f.core_principle} (Use when: {f.application_criteria})\n"

        system_prompt = (
            "You are JAY's Polymath Engine. You act as an elite mentor by applying mental models of world-class experts to the Founder's current priority.\n\n"
            f"{fw_text}\n\n"
            "INSTRUCTIONS:\n"
            "1. Select the SINGLE most relevant mental model from the list above that applies to the user's action.\n"
            "2. Apply that specific framework to provide highly actionable advice on how to execute this action.\n"
            "3. Return a strictly valid JSON object with the following schema:\n"
            '{"expert_name": "Name of the expert", "framework_name": "Name of the framework", "advice": "2-3 sentences of specific, actionable advice based solely on their core principle."}'
        )

        user_prompt = f"TARGET ACTION: {statement}\nCONTEXT/REASON: {context}\n"

        settings = get_settings()

        try:
            import asyncio
            from jay.engines.llm import generate_chat
            
            def _run_llm():
                return generate_chat(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2
                )
                
            response = await asyncio.to_thread(_run_llm)
            content = response["choices"][0]["message"]["content"].strip()
            
            import json
            import re

            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
                
            data = json.loads(content.strip())

            return ExpertAdvice(
                expert_name=data.get("expert_name", "Unknown"),
                framework_name=data.get("framework_name", "General Wisdom"),
                advice=data.get("advice", "Execute efficiently."),
            )
        except Exception as e:
            print(f"PolymathEngine Error: {e}")
            return None

    async def run_website_review_board(self, ui_code: str) -> str:
        """Runs the 5-expert panel on proposed UI code according to the Website Constitution."""
        from jay.engines.llm import get_llama
        import asyncio
        import os
        
        # Load constitution
        constitution_text = "Standard Rules"
        docs_path = os.path.join(os.path.dirname(__file__), "../../../docs/JAY_WEBSITE_CONSTITUTION.md")
        if os.path.exists(docs_path):
            with open(docs_path, "r") as f:
                constitution_text = f.read()

        system_prompt = (
            "You are the JAY Website Review Board, consisting of 5 Silicon Valley experts: "
            "Design, UX, Engineering, Conversion, and Brand.\n"
            f"Evaluate the following UI code strictly against the JAY Website Constitution:\n\n{constitution_text}\n\n"
            "Provide a short brutally honest critique from each of the 5 experts, and a final verdict of 'APPROVED' or 'REJECTED'."
        )
        
        def _run_llm():
            return generate_chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"UI CODE TO REVIEW:\n{ui_code}"},
                ],
                temperature=0.1
            )
            
        try:
            response = await asyncio.to_thread(_run_llm)
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Review Board Error: {e}"
