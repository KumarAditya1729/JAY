# JAY

Joint Artificial You.

JAY is a local-first sovereign human operating system for one Founder. This repository starts with Phase 1: the Memory Core.

## North Star

JAY answers one question with increasing accuracy over time:

> What is the highest leverage action available to the Founder right now?

The system optimizes for Founder Leverage Ratio, not scale.

## Phase 1 Scope

Memory Core preserves and retrieves:

- Projects
- People
- Meetings
- Ideas
- Tasks
- Lessons
- Commitments
- Documents
- Decisions

The first service exposes ingestion, event audit, timeline retrieval, and natural-language search hooks. Graph and vector projections are designed as downstream projections from the immutable event log.

## Local Development

```bash
cp .env.example .env
docker compose up -d
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn jay.api.main:app --reload
```

API docs will be available at `http://127.0.0.1:8000/docs`.

## Architecture

JAY follows the hierarchy:

1. Intent
2. Trust
3. Memory
4. Intelligence
5. Execution
6. Continuity
7. Evolution

No feature may bypass this order.

See [docs/ARCHITECTURE.md](/Users/adityashrivastava/Desktop/JAY/docs/ARCHITECTURE.md) and [docs/PHASE_1_MEMORY_CORE.md](/Users/adityashrivastava/Desktop/JAY/docs/PHASE_1_MEMORY_CORE.md).

