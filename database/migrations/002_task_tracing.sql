-- ─────────────────────────────────────────────────────────────
--  AUTO-PILOT  ·  Migration 002
--  Add agent_trace_id and tokens_used to tasks table
--  Run: psql $DATABASE_URL -f database/migrations/002_task_tracing.sql
-- ─────────────────────────────────────────────────────────────

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'agent_trace_id'
    ) THEN
        ALTER TABLE tasks ADD COLUMN agent_trace_id TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'tokens_used'
    ) THEN
        ALTER TABLE tasks ADD COLUMN tokens_used INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'duration_ms'
    ) THEN
        ALTER TABLE tasks ADD COLUMN duration_ms INTEGER;
    END IF;
END $$;
