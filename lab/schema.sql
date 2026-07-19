BEGIN;

CREATE TABLE IF NOT EXISTS owners (
    id integer PRIMARY KEY,
    name text NOT NULL,
    team text NOT NULL,
    email text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS assets (
    id integer PRIMARY KEY,
    hostname text NOT NULL UNIQUE,
    environment text NOT NULL CHECK (environment IN ('production', 'staging', 'development')),
    owner_id integer NOT NULL REFERENCES owners(id),
    criticality text NOT NULL CHECK (criticality IN ('critical', 'high', 'medium', 'low')),
    created_at timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS maintenance_events (
    id integer PRIMARY KEY,
    asset_id integer NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    event_type text NOT NULL,
    status text NOT NULL CHECK (status IN ('completed', 'scheduled', 'failed')),
    performed_at timestamptz NOT NULL,
    notes text NOT NULL
);

CREATE INDEX IF NOT EXISTS maintenance_events_asset_id_idx
    ON maintenance_events(asset_id);

COMMIT;
