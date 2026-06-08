# Security Doctrine

## Requirements

- Local first.
- Encryption at rest.
- Encryption in transit.
- Audit everything.
- Immutable logs.
- Human override.
- Offline recovery.

## Initial Local Controls

- Databases run locally through Docker Compose.
- Secrets are read from `.env`, never committed.
- Event log is append-only by convention and should be hardened with database roles before production use.
- Object storage keeps original artifacts separate from derived summaries.

## Next Hardening Steps

1. Add database roles that deny update/delete on `event_log`.
2. Add signed event hashes and hash chaining.
3. Add encrypted object storage buckets.
4. Add offline backup scripts with restore drills.
5. Add Guardian audit jobs.

