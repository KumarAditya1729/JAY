# JAY Architecture

## Design Bias

JAY is built for one Founder. Every subsystem optimizes for trust, continuity, and leverage over generality.

## Layer Hierarchy

1. **Intent**: mission, values, goals, non-negotiables, and current strategic context.
2. **Trust**: confidence, assumptions, risks, reversibility, evidence, and auditability.
3. **Memory**: permanent capture of facts, events, commitments, decisions, and documents.
4. **Intelligence**: retrieval, synthesis, pattern recognition, and recommendation.
5. **Execution**: approval-gated action and workflow coordination.
6. **Continuity**: operating modes for absence, travel, illness, and emergency.
7. **Evolution**: monthly improvement proposals with Founder approval.

## Local-First Storage

- PostgreSQL: event log, projections, audit records, timeline search.
- Neo4j: relationship graph and mission/project/person topology.
- Qdrant: semantic search over memory and documents.
- Redis: short-lived coordination, cache, and queue state.
- Object storage: original documents, meeting artifacts, media, and exports.

## Event Sourcing

Every important action is appended to `event_log` before it is projected elsewhere.

Events are immutable. Corrections are new events.

Projection stores may be rebuilt from events:

- `memory_items`
- graph nodes and edges
- vector embeddings
- dashboard summaries
- trust ledgers

## Founder Authority

The Founder is the only root authority. Any future agent, automation, or digital twin can recommend, prepare, or simulate, but execution requires explicit authority unless the action is pre-approved by policy.

## Guardian System

Guardian is separate from JAY's recommendation path. It audits recommendations, detects misalignment, challenges assumptions, and monitors trust degradation. It must never be implemented as self-review inside the same agent loop.

