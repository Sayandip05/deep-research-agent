-- ─────────────────────────────────────────────────────────────
--  AUTO-PILOT  ·  Migration 001
--  Add price_history table and missing indexes
--  Run: psql $DATABASE_URL -f database/migrations/001_price_history.sql
-- ─────────────────────────────────────────────────────────────

-- price_history is defined in schema.sql but added here for
-- environments that only ran an earlier version of the schema.

CREATE TABLE IF NOT EXISTS price_history (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    track_id        UUID NOT NULL REFERENCES price_tracks(id) ON DELETE CASCADE,
    price           NUMERIC(10, 2) NOT NULL,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_price_history_track
    ON price_history(track_id, recorded_at DESC);

-- Add schedule_id FK to price_tracks if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'price_tracks' AND column_name = 'schedule_id'
    ) THEN
        ALTER TABLE price_tracks ADD COLUMN schedule_id UUID REFERENCES schedules(id) ON DELETE SET NULL;
    END IF;
END $$;
