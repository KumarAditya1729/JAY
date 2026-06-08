import sys
from jay.db import SessionLocal
from jay.events.service import EventService
from jay.import_engine import ImportEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_projects.py <path_to_csv>")
        sys.exit(1)
        
    engine = ImportEngine()
    rows = engine.load_csv(sys.argv[1])
    if not rows:
        sys.exit(1)

    with SessionLocal() as session:
        event_service = EventService(session)
        
        def process(row):
            if not row.get('id'):
                raise ValueError("Missing project id")
                
            payload = {
                "id": row['id'],
                "impact": int(row.get('impact', 3))
            }
            event_service.record(
                stream_id=f"project_{row['id']}",
                event_type="project.imported",
                actor_id="system",
                payload=payload,
                entity_type="project",
                entity_id=row['id']
            )
                
        engine.run_import(rows, process)
        session.commit()
        
    engine.print_report()

if __name__ == "__main__":
    main()
