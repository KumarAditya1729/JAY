from enum import Enum
from jay.tools.schemas import ToolManifest

class PolicyVerdict(Enum):
    AUTO_APPROVE = "AUTO_APPROVE"
    FOUNDER_APPROVAL = "FOUNDER_APPROVAL"
    BLOCKED = "BLOCKED"

class ExecutionPolicyEngine:
    @staticmethod
    def evaluate(manifest: ToolManifest, arguments: dict = None) -> PolicyVerdict:
        """
        Evaluates a tool invocation against the JAY OMEGA Trust Gate.
        """
        if manifest.risk_score >= 0.8:
            return PolicyVerdict.BLOCKED
            
        if manifest.risk_score >= 0.3:
            return PolicyVerdict.FOUNDER_APPROVAL
            
        return PolicyVerdict.AUTO_APPROVE

class RealityCheckEngine:
    @staticmethod
    def verify_completion(task_description: str, agent_result: str) -> bool:
        """
        In a production Reality Engine, this would query Qdrant or recent webhooks 
        to ensure physical evidence (e.g. a Git commit, a Vercel deployment URL) 
        exists to support the agent's claim that a task is 'done'.
        For now, we enforce a strict heuristic: the result must contain physical proof 
        (e.g., URLs, commit hashes, or IDs).
        """
        # Placeholder strict rule: Result must have substantive length or contain links/paths
        if len(agent_result) < 20 and "http" not in agent_result and "/" not in agent_result:
            return False
        return True
