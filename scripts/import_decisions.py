import sys
from datetime import datetime
from jay.db import SessionLocal
from jay.decisions.service import DecisionService
from jay.decisions.schemas import DecisionCreate
from jay.import_engine import ImportEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_decisions.py <path_to_csv>")
        sys.exit(1)
        
    engine = ImportEngine()
    rows = engine.load_csv(sys.argv[1])
    if not rows:
        sys.exit(1)

    with SessionLocal() as session:
        service = DecisionService(session)
        
        def process(row):
            if not row.get('statement'):
                raise ValueError("Missing decision statement")
                
            options = [{"description": o.strip()} for o in row.get('options_considered', '').split(',') if o.strip()]
            risks = [{"description": r.strip()} for r in row.get('risks', '').split(',') if r.strip()]
            
            dt = datetime.now()
            if row.get('decision_date'):
                try:
                    dt = datetime.fromisoformat(row['decision_date'])
                except:
                    pass
            
            decision = DecisionCreate(
                statement=row['statement'],
                decision_type=row.get('type', 'strategic'),
                maker="founder",
                decision_date=dt,
                options_considered=options,
                risks=risks,
                expected_outcome=row.get('expected_outcome'),
                reversibility_score=0.2 if row.get('reversibility') == 'Low' else 0.8,
                success_criteria=row.get('success_criteria')
            )
            service.record_decision(decision, actor_id="founder")
                
        engine.run_import(rows, process)
        session.commit()
        
    engine.print_report()

if __name__ == "__main__":
    main()
