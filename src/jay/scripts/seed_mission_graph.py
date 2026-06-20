from jay.db import SessionLocal, engine, Base
from jay.engines.models import (
    MissionLedger,
    ProjectLedger,
    TaskLedger,
    DependencyLedger,
)


def seed_graph():
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if already seeded
    existing = (
        db.query(MissionLedger).filter(MissionLedger.title == "Build JAY OMEGA").first()
    )
    if existing:
        print("Graph already seeded.")
        return

    # 1. Create Mission
    mission = MissionLedger(
        title="Build JAY OMEGA",
        description="Build the Sovereign Human Operating System",
        health_score=85.0,
    )
    db.add(mission)
    db.flush()

    # 2. Create Project
    project = ProjectLedger(
        mission_id=mission.id,
        title="Phase 7.0 Mission & Business OS",
        momentum_score=95.0,
    )
    db.add(project)
    db.flush()

    # 3. Create Tasks
    task_schema = TaskLedger(
        project_id=project.id,
        statement="Update Database Schema with Graph Ledgers",
        urgency=10.0,
        impact=9.0,
        status="SUCCESS",
    )
    task_engine = TaskLedger(
        project_id=project.id,
        statement="Implement BusinessEngine bottlenecks",
        urgency=8.0,
        impact=8.5,
        status="Pending",
    )
    task_ui = TaskLedger(
        project_id=project.id,
        statement="Build Mission Graph UI in React",
        urgency=9.0,
        impact=7.5,
        status="Pending",
    )
    db.add_all([task_schema, task_engine, task_ui])
    db.flush()

    # 4. Create Dependency (UI is blocked by Engine)
    dep = DependencyLedger(task_id=task_ui.id, blocked_by_task_id=task_engine.id)
    db.add(dep)

    db.commit()
    print("Mission Graph seeded successfully!")


if __name__ == "__main__":
    seed_graph()
