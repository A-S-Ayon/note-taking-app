-- ============================================================
--  NoteVault – Supabase SQL Setup
--  Run this in: Supabase Dashboard → SQL Editor → New Query
-- ============================================================

-- 1. Users table (stores hashed passwords — NOT using Supabase Auth)
CREATE TABLE IF NOT EXISTS users (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email      TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,         -- bcrypt hash
    full_name  TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Notes table
CREATE TABLE IF NOT EXISTS notes (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title      TEXT NOT NULL DEFAULT 'Untitled',
    content    TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Auto-update updated_at on notes
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER notes_updated_at
    BEFORE UPDATE ON notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 4. Index for fast per-user note lookup
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);

-- 5. Row Level Security — DISABLE for service_role key usage (our FastAPI backend)
--    The service_role key bypasses RLS, so policies aren't strictly needed,
--    but enabling RLS + policies is good practice if you ever expose the anon key.
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE notes DISABLE ROW LEVEL SECURITY;

-- Done! ✅
