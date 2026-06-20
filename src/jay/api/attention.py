from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from jay.db import get_session
from jay.engines.models import WorkSessionLedger, MissionLedger
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/attention", tags=["Attention OS"])


@router.get("/audit")
async def get_attention_audit(session: Session = Depends(get_session)):
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    sessions = (
        session.query(WorkSessionLedger)
        .filter(WorkSessionLedger.start_time >= one_week_ago)
        .all()
    )

    missions = session.query(MissionLedger).all()
    mission_text = "\n".join([f"- {m.title}: {m.description}" for m in missions])
    if not mission_text:
        mission_text = "No active missions declared."

    session_data = []
    for s in sessions:
        # Timezone-aware calculation
        start_tz = s.start_time
        if start_tz.tzinfo is None:
            start_tz = start_tz.replace(tzinfo=timezone.utc)

        end_tz = s.end_time
        if end_tz:
            if end_tz.tzinfo is None:
                end_tz = end_tz.replace(tzinfo=timezone.utc)
            dur = (end_tz - start_tz).total_seconds() / 3600
        else:
            dur = (datetime.now(timezone.utc) - start_tz).total_seconds() / 3600

        session_data.append(
            f"Duration: {dur:.1f}hrs | Summary: {s.session_summary or 'Unsummarized or active'}"
        )

    session_log = "\n".join(session_data)
    if not session_log:
        session_log = "No work sessions recorded this week."

    system_prompt = (
        "You are JAY's Attention OS.\n"
        "Your job is to audit the founder's time allocation over the last week and provide BRUTAL, honest feedback.\n"
        f"The founder's declared missions are:\n{mission_text}\n\n"
        f"The founder's actual work sessions this week:\n{session_log}\n\n"
        "Write a 2-3 paragraph critique. Identify focus fragmentation, mission drift, or overengineering. "
        "Point out discrepancies between their declared missions and actual time spent."
    )

    try:
        import asyncio
        from jay.engines.llm import generate_chat
        
        def _run_llm():
            return generate_chat(
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.2
            )
            
        response = await asyncio.to_thread(_run_llm)
        critique = response["choices"][0]["message"]["content"].strip()
        return {"audit_text": critique}
    except Exception as e:
        return {
            "audit_text": f"Attention OS failed to connect to local intelligence engine: {e}"
        }
