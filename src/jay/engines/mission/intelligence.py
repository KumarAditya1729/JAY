from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from jay.db import SessionLocal
from jay.engines.models import (
    MissionLedger,
    ProjectLedger,
    TaskLedger,
    DependencyLedger,
)

class MissionIntelligenceEngine:
    @staticmethod
    def analyze_missions(db_session=None):
        if db_session is not None:
            return MissionIntelligenceEngine._do_analyze(db_session)

        with SessionLocal() as db:
            return MissionIntelligenceEngine._do_analyze(db)

    @staticmethod
    def _do_analyze(db):
        """
        Analyzes all active missions, returning their health, forecasted stall state,
        and strategic bottlenecks.
        """
        results = []
        missions = db.query(MissionLedger).filter(MissionLedger.status == "Active").all()
        for mission in missions:
            projects = db.query(ProjectLedger).filter(ProjectLedger.mission_id == mission.id, ProjectLedger.status == "Active").all()
            project_data = []

            mission_health = 0.0

            for project in projects:
                velocity = MissionIntelligenceEngine.calculate_task_velocity(db, project.id)
                forecast = MissionIntelligenceEngine.forecast_momentum(db, project.id, velocity)
                
                project_data.append({
                    "project": project,
                    "velocity": velocity,
                    "forecast": forecast
                })
                
                if forecast == "Stall":
                    mission_health -= 10.0
                elif forecast == "Accelerating":
                    mission_health += 10.0
                    
                mission_health += project.momentum_score
                
            mission_health = max(0.0, mission_health / max(len(projects), 1))
            mission.health_score = mission_health

            bottlenecks = MissionIntelligenceEngine.identify_bottlenecks(db, [p.id for p in projects])

            results.append({
                "mission": mission,
                "projects": project_data,
                "bottlenecks": bottlenecks
            })

        return results

    @staticmethod
    def calculate_task_velocity(db, project_id) -> float:
        """
        Calculates the velocity of tasks closed over the last 14 days.
        Returns closed tasks per day.
        """
        two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
        # For this prototype, we'll assume SUCCESS status means closed.
        # Ideally, we'd check an `updated_at` or `closed_at` column, but we will count how many are success.
        closed_count = db.query(TaskLedger).filter(
            TaskLedger.project_id == project_id,
            TaskLedger.status == "SUCCESS"
        ).count()
        # Mocking a velocity based on total closed vs time, or just closed_count / 14
        return round(closed_count / 14.0, 2)

    @staticmethod
    def forecast_momentum(db, project_id, velocity: float) -> str:
        """
        Predicts if the project is Stalling, Stable, or Accelerating.
        """
        pending_count = db.query(TaskLedger).filter(
            TaskLedger.project_id == project_id,
            TaskLedger.status != "SUCCESS"
        ).count()
        
        if pending_count > 0 and velocity == 0.0:
            return "Stall"
        elif pending_count > 0 and (pending_count / max(velocity, 0.1)) > 30:
            return "At Risk"
        elif velocity > 0.5:
            return "Accelerating"
        return "Stable"

    @staticmethod
    def identify_bottlenecks(db, project_ids: list):
        """
        Identifies tasks that block the most critical/urgent tasks in a set of projects.
        """
        if not project_ids:
            return []
            
        bottlenecks = (
            db.query(
                DependencyLedger.blocked_by_task_id,
                func.count(DependencyLedger.id).label("block_count"),
            )
            .join(TaskLedger, TaskLedger.id == DependencyLedger.task_id)
            .filter(TaskLedger.project_id.in_(project_ids))
            .group_by(DependencyLedger.blocked_by_task_id)
            .having(func.count(DependencyLedger.id) > 0)
            .all()
        )
        
        results = []
        for b in bottlenecks:
            task = db.query(TaskLedger).filter(TaskLedger.id == b.blocked_by_task_id).first()
            if task and task.status != "SUCCESS":
                # Calculate blast radius impact
                blocked_tasks = db.query(TaskLedger).join(
                    DependencyLedger, DependencyLedger.task_id == TaskLedger.id
                ).filter(DependencyLedger.blocked_by_task_id == task.id).all()
                
                blast_radius_impact = sum([t.impact * t.urgency for t in blocked_tasks])
                
                results.append({
                    "task": task,
                    "blocks_count": b.block_count,
                    "blast_radius_impact": blast_radius_impact
                })
                
        # Sort by blast radius impact
        results.sort(key=lambda x: x["blast_radius_impact"], reverse=True)
        return results
