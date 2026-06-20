from jay.db import SessionLocal
from jay.engines.models import ResearchLedger

class ResearchOSEngine:
    @staticmethod
    def get_research_queue() -> list[dict]:
        """
        Retrieves the active and recently completed research tasks.
        In a real production system, this engine would also contain the `execute_research`
        loop running in a background Celery worker, performing searches and LLM synthesis.
        """
        with SessionLocal() as db:
            research_items = db.query(ResearchLedger).order_by(ResearchLedger.created_at.desc()).limit(5).all()
            
            results = []
            for item in research_items:
                results.append({
                    "id": str(item.id),
                    "query": item.query,
                    "trigger_source": item.trigger_source,
                    "status": item.status,
                    "synthesis_report": item.synthesis_report,
                    "sources_cited": item.sources_cited or []
                })
            return results
