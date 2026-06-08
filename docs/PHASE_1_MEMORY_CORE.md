# Phase 1: Memory Core

## Mission

Ensure no important information is ever lost.

## First Principles

- Memory before automation.
- Audit before convenience.
- Original source before summary.
- Corrections never overwrite history.
- Every memory item should connect to a person, project, decision, task, document, or commitment when possible.

## Memory Types

- `project`
- `person`
- `meeting`
- `idea`
- `task`
- `lesson`
- `commitment`
- `document`
- `decision`

## Capture Contract

Each memory item stores:

- `kind`
- `title`
- `body`
- `source`
- `importance`
- `confidence`
- `occurred_at`
- `tags`
- `linked_entity_ids`

Each capture emits `memory.item_recorded`.

## Search Contract

Phase 1 search has two layers:

- PostgreSQL full-text and timeline search.
- Qdrant semantic search projection.

PostgreSQL search is the source-of-truth retrieval path for the first implementation. Qdrant should be treated as a projection that improves recall, not as canonical memory.

## Decision Recall

Decisions must preserve:

- decision statement
- options considered
- evidence
- assumptions
- risks
- reversibility
- expected impact
- final authority

## Relationship Mapping

Graph projection should connect:

- people to projects
- meetings to people
- decisions to projects and goals
- commitments to people and due dates
- documents to source events

