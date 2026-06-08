# Event Sourcing Maturity

## Event Lifecycle

1. **Ingestion**: An action occurs via the API (e.g., creating a memory item).
2. **Event Creation**: Instead of directly modifying the projection tables, an `EventLog` entry is constructed containing the immutable facts (`payload`) and auditing metadata (`trust`, `actor_id`).
3. **Commit**: The event is appended to the `event_log` table.
4. **Projection Dispatch**: The event is handed off to registered Projectors.

## Projection Lifecycle

1. **Handling**: Each projector (`MemoryProjector`, `GraphProjector`, etc.) receives the event.
2. **Idempotency Check**: Projectors must gracefully handle receiving the same event twice.
3. **State Update**: The projector translates the event into the optimized read model (e.g., inserting a row into `memory_items` or a node into Neo4j).
4. **Synchronous vs Asynchronous**: Currently, the Memory Projection is updated synchronously within the same transaction as the event append. Future projections (Graph, Vector) may be updated asynchronously.

## Replay Strategy

Because the `event_log` is immutable and complete, any projection can be deleted and rebuilt from scratch.

1. **Reset**: The Replay Engine calls `reset()` on the target projector. For PostgreSQL projections, this usually means `TRUNCATE TABLE ...`.
2. **Stream**: The Engine streams all events from `event_log` ordered by `occurred_at` ascending.
3. **Apply**: Each event is passed to the projector's `handle()` method.
4. **Commit**: The engine commits the rebuilt state in batches.

You can trigger this manually via the CLI:
```bash
python -m jay.cli rebuild-memory
python -m jay.cli rebuild-graph
python -m jay.cli rebuild-vectors
python -m jay.cli rebuild-all
```

## Failure Recovery

- **Corrupt Projections**: If a projection gets corrupted (e.g., bad migration or manual tampering), simply run the corresponding `rebuild-<projection>` CLI command to recreate it from the source of truth.
- **Projector Bugs**: If a bug is found in how an event was projected, fix the projector code, deploy, and run the rebuild CLI command. The historical events will be correctly interpreted by the new logic.
- **Event Log Immutability**: The `event_log` must never be updated or deleted. Database roles should enforce this. If incorrect data is ingested, a compensating event should be appended.
