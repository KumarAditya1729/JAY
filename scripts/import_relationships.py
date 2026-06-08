import sys
from jay.db import SessionLocal
from jay.events.service import EventService
from jay.import_engine import ImportEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_relationships.py <path_to_csv>")
        sys.exit(1)
        
    engine = ImportEngine()
    rows = engine.load_csv(sys.argv[1])
    if not rows:
        sys.exit(1)

    with SessionLocal() as session:
        event_service = EventService(session)
        
        def process(row):
            if not row.get('person'):
                raise ValueError("Missing person name")
                
            payload = {
                "person": row['person'],
                "role": row.get('role', 'Connection'),
                "trust_level": float(row.get('trust_level', 0.5))
            }
            event_service.record(
                stream_id=f"relationship_{row['person']}",
                event_type="relationship.imported",
                actor_id="system",
                payload=payload,
                entity_type="relationship",
                entity_id=row['person']
            )
                
        engine.run_import(rows, process)
        session.commit()
        
    engine.print_report()

if __name__ == "__main__":
    main()
