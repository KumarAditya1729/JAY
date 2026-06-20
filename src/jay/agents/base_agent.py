import uuid
import hashlib
from datetime import datetime
from jay.db import SessionLocal
from jay.engines.models import RealityProofLedger
from jay.engines.autonomy_governance import AutonomyGovernanceEngine

class BaseAgent:
    def __init__(self, role_name: str):
        self.role_name = role_name

    def execute(self, domain: str, required_level: int, action_description: str, mock_proof_url: str) -> dict:
        """
        The strict execution loop for an Autonomous Agent.
        1. Checks Governance
        2. Executes
        3. Creates Reality Proof
        """
        # 1. Trust Gate Check
        is_approved = AutonomyGovernanceEngine.check_permission(domain, required_level)
        
        if not is_approved:
            return {
                "status": "BLOCKED",
                "reason": f"Governance Trust Gate denied. Required Level {required_level} for domain '{domain}'.",
                "proof": None
            }
            
        # 2. Execution (Mocked)
        # In a real system, the agent calls GitHub API, sends emails, etc.
        
        # 3. Create Reality Proof
        execution_id = uuid.uuid4()
        proof_hash = hashlib.sha256(f"{execution_id}:{mock_proof_url}:{datetime.now().isoformat()}".encode()).hexdigest()
        
        with SessionLocal() as db:
            proof = RealityProofLedger(
                id=uuid.uuid4(),
                execution_id=execution_id,
                agent_role=self.role_name,
                action_taken=action_description,
                proof_url=mock_proof_url,
                proof_hash=proof_hash,
                verified=True
            )
            db.add(proof)
            db.commit()
            
            proof_id = str(proof.id)

        return {
            "status": "SUCCESS",
            "execution_id": str(execution_id),
            "proof_id": proof_id,
            "proof_url": mock_proof_url,
            "proof_hash": proof_hash
        }
