CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS event_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    causation_id UUID,
    correlation_id UUID,
    payload JSONB NOT NULL,
    trust JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_event_log_stream ON event_log (stream_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_event_log_entity ON event_log (entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_event_log_type_time ON event_log (event_type, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_event_log_payload_gin ON event_log USING GIN (payload);

CREATE OR REPLACE FUNCTION immutable_array_to_string(text[], text)
RETURNS text AS $$
    SELECT array_to_string($1, $2);
$$ LANGUAGE sql IMMUTABLE;

CREATE TABLE IF NOT EXISTS memory_items (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    source TEXT NOT NULL,
    importance INTEGER NOT NULL DEFAULT 3,
    confidence NUMERIC(4, 3) NOT NULL DEFAULT 0.700,
    occurred_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    tags TEXT[] NOT NULL DEFAULT '{}',
    linked_entity_ids TEXT[] NOT NULL DEFAULT '{}',
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(body, '')), 'B') ||
        setweight(to_tsvector('english', immutable_array_to_string(tags, ' ')), 'C')
    ) STORED
);

CREATE INDEX IF NOT EXISTS idx_memory_items_kind ON memory_items (kind);
CREATE INDEX IF NOT EXISTS idx_memory_items_occurred ON memory_items (occurred_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_memory_items_search ON memory_items USING GIN (search_vector);

CREATE TABLE IF NOT EXISTS trust_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    confidence_score NUMERIC(4, 3) NOT NULL,
    risk_score NUMERIC(4, 3) NOT NULL,
    impact_score NUMERIC(4, 3) NOT NULL,
    reversibility_score NUMERIC(4, 3) NOT NULL,
    evidence_score NUMERIC(4, 3) NOT NULL,
    assumptions TEXT[] NOT NULL DEFAULT '{}',
    evidence TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_trust_ledger_entity ON trust_ledger (entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_trust_ledger_created ON trust_ledger (created_at DESC);

CREATE TABLE IF NOT EXISTS intent_nodes (
    id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS intent_edges (
    source_id TEXT NOT NULL REFERENCES intent_nodes(id) ON DELETE CASCADE,
    target_id TEXT NOT NULL REFERENCES intent_nodes(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (source_id, target_id, relationship_type)
);

CREATE INDEX IF NOT EXISTS idx_intent_nodes_type ON intent_nodes (node_type);

CREATE TABLE IF NOT EXISTS leverage_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    hours_saved NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    knowledge_preserved_score NUMERIC(4, 3) NOT NULL DEFAULT 0.000,
    decisions_improved_score NUMERIC(4, 3) NOT NULL DEFAULT 0.000,
    risks_avoided_score NUMERIC(4, 3) NOT NULL DEFAULT 0.000,
    opportunities_captured_score NUMERIC(4, 3) NOT NULL DEFAULT 0.000,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_leverage_ledger_entity ON leverage_ledger (entity_type, entity_id);

CREATE TABLE IF NOT EXISTS decision_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    statement TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    decision_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    maker TEXT NOT NULL,
    options_considered JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    assumptions JSONB NOT NULL DEFAULT '[]'::jsonb,
    risks JSONB NOT NULL DEFAULT '[]'::jsonb,
    expected_outcome TEXT,
    success_criteria TEXT,
    reversibility_score NUMERIC(4, 3) NOT NULL DEFAULT 0.500,
    intent_alignment_score NUMERIC(4, 3) NOT NULL DEFAULT 0.500,
    trust_envelope TEXT,
    outcome_status TEXT NOT NULL DEFAULT 'Pending',
    actual_outcome TEXT,
    lessons_learned TEXT,
    outcome_date TIMESTAMPTZ,
    linked_entity_ids TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_decision_ledger_maker ON decision_ledger (maker);
CREATE INDEX IF NOT EXISTS idx_decision_ledger_date ON decision_ledger (decision_date DESC);
CREATE INDEX IF NOT EXISTS idx_decision_ledger_outcome ON decision_ledger (outcome_status);

CREATE TABLE IF NOT EXISTS founder_profile (
    id TEXT PRIMARY KEY DEFAULT 'default',
    risk_tolerance TEXT,
    time_horizon TEXT,
    decision_style TEXT,
    communication_style TEXT,
    leadership_style TEXT,
    learning_style TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS behavior_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action TEXT NOT NULL,
    recommendation TEXT,
    response TEXT,
    outcome TEXT,
    context JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_behavior_ledger_time ON behavior_ledger (occurred_at DESC);

CREATE TABLE IF NOT EXISTS preference_edges (
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    weight NUMERIC(5, 3) NOT NULL DEFAULT 1.000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (source_id, target_id, relationship_type)
);

