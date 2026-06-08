from collections import defaultdict
from sqlalchemy.orm import Session

from jay.memory.models import MemoryItem


class PrioritizationEngine:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> dict:
        items = self.session.query(MemoryItem).filter(MemoryItem.importance >= 4).all()
        
        # What kinds of high-importance items does the founder store?
        kind_counts = defaultdict(int)
        for item in items:
            kind_counts[item.kind] += 1
            
        priorities = sorted(kind_counts.items(), key=lambda x: x[1], reverse=True)
        
        top_priorities = []
        for kind, count in priorities[:3]:
            top_priorities.append(f"Highly prioritizes {kind}s ({count} high-importance items)")
            
        if not top_priorities:
            top_priorities.append("Not enough data to determine priorities.")
            
        return {
            "top_priorities": top_priorities,
            "distribution": dict(kind_counts)
        }
