import sys
from pathlib import Path
from jay.db import SessionLocal
from jay.memory.service import MemoryService
from jay.memory.schemas import MemoryCreate
from jay.import_engine import ImportEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_memories.py <path_to_csv>")
        sys.exit(1)
        
    engine = ImportEngine()
    rows = engine.load_csv(sys.argv[1])
    if not rows:
        sys.exit(1)

    with SessionLocal() as session:
        service = MemoryService(session)
        
        def process(row):
            if not row.get('title') or not row.get('body'):
                raise ValueError("Missing title or body")
                
            tags = [t.strip() for t in row.get('tags', '').split(',') if t.strip()]
            intents = [t.strip() for t in row.get('intent_ids', '').split(',') if t.strip()]
            
            from jay.memory.schemas import TrustEnvelope
            trust = TrustEnvelope(aligned_intent_ids=intents)
            
            memory = MemoryCreate(
                kind=row.get('kind', 'note'),
                title=row['title'],
                body=row['body'],
                source=row.get('source', 'Manual Import'),
                importance=int(row.get('importance', 3) if str(row.get('importance', '3')).isdigit() else 3),
                tags=tags,
                trust=trust
            )
            service.record(memory)
                
        engine.run_import(rows, process)
        session.commit()
        
    engine.print_report()

if __name__ == "__main__":
    main()
