BEGIN;

TRUNCATE TABLE maintenance_events, assets, owners RESTART IDENTITY CASCADE;

INSERT INTO owners (id, name, team, email) VALUES
    (1, 'Maya Chen', 'Platform Engineering', 'maya.chen@example.test'),
    (2, 'Noah Williams', 'Database Operations', 'noah.williams@example.test'),
    (3, 'Priya Raman', 'Security Operations', 'priya.raman@example.test'),
    (4, 'Luis Martinez', 'Application Reliability', 'luis.martinez@example.test');

INSERT INTO assets (id, hostname, environment, owner_id, criticality, created_at) VALUES
    (1, 'api-prod-01', 'production', 4, 'critical', '2026-01-05T09:00:00Z'),
    (2, 'api-prod-02', 'production', 4, 'critical', '2026-01-05T09:05:00Z'),
    (3, 'db-prod-01', 'production', 2, 'critical', '2026-01-04T15:00:00Z'),
    (4, 'worker-prod-01', 'production', 1, 'high', '2026-01-06T10:00:00Z'),
    (5, 'api-stage-01', 'staging', 1, 'medium', '2026-01-07T11:00:00Z'),
    (6, 'scanner-dev-01', 'development', 3, 'low', '2026-01-08T12:00:00Z');

INSERT INTO maintenance_events
    (id, asset_id, event_type, status, performed_at, notes)
VALUES
    (1, 1, 'security_patch', 'completed', '2026-06-01T02:05:00Z', 'June security baseline'),
    (2, 2, 'security_patch', 'completed', '2026-06-01T02:11:00Z', 'June security baseline'),
    (3, 3, 'backup_test', 'completed', '2026-06-03T04:30:00Z', 'Logical restore verified'),
    (4, 4, 'configuration', 'completed', '2026-06-05T18:00:00Z', 'Worker concurrency adjusted'),
    (5, 5, 'deployment', 'completed', '2026-06-09T16:20:00Z', 'Release candidate deployed'),
    (6, 6, 'scanner_update', 'completed', '2026-06-11T20:15:00Z', 'Signature set refreshed'),
    (7, 1, 'certificate', 'completed', '2026-07-01T01:10:00Z', 'TLS certificate rotated'),
    (8, 2, 'certificate', 'completed', '2026-07-01T01:18:00Z', 'TLS certificate rotated'),
    (9, 3, 'index_maintenance', 'completed', '2026-07-03T03:45:00Z', 'Indexes analyzed'),
    (10, 4, 'security_patch', 'completed', '2026-07-06T02:15:00Z', 'July security baseline'),
    (11, 5, 'disaster_rehearsal', 'completed', '2026-07-10T17:30:00Z', 'Recovery path exercised'),
    (12, 6, 'scanner_update', 'scheduled', '2026-08-01T20:00:00Z', 'Next signature refresh');

COMMIT;
