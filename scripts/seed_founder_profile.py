import sys
from pathlib import Path
from jay.db import SessionLocal
from jay.intent.service import IntentService
from jay.intent.schemas import IntentNodeCreate, IntentNodeType
from jay.import_engine import ImportEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed_founder_profile.py <path_to_json>")
        sys.exit(1)
        
    engine = ImportEngine()
    data = engine.load_json(sys.argv[1])
    if not data:
        sys.exit(1)

    with SessionLocal() as session:
        service = IntentService(session)
        
        def process(item_tuple):
            kind, statement = item_tuple
            node = IntentNodeCreate(
                node_type=IntentNodeType(kind),
                title=statement[:50],  # Short title
                description=statement
            )
            service.create_node(node)
            
        items = []
        for kind in ["mission", "values", "goals", "non_negotiables"]:
            # mapped to Intent types
            kind_map = {
                "mission": "mission",
                "values": "value",
                "goals": "goal",
                "non_negotiables": "non_negotiable"
            }
            mapped_kind = kind_map[kind]
            for statement in data.get(kind, []):
                items.append((mapped_kind, statement))
                
        engine.run_import(items, process)
        session.commit()
        
    engine.print_report()

if __name__ == "__main__":
    main()
