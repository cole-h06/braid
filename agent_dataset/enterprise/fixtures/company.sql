CREATE TABLE policy_config (
    record_id TEXT PRIMARY KEY,
    attribute TEXT NOT NULL,
    value TEXT NOT NULL,
    source_modified_at TEXT NOT NULL,
    origin_id TEXT NOT NULL,
    upstream_source_id TEXT
);


INSERT INTO policy_config VALUES
    ('policy-001', 'return_window', '30 days', '2026-02-02T09:30:00Z', 'ops_config_2026_02', 'handbook'),
    ('policy-002', 'warranty', '2 years', '2026-02-02T09:30:00Z', 'ops_config_2026_02', 'handbook'),
    ('policy-003', 'shipping_fee', 'customer pays', '2026-02-02T09:30:00Z', 'ops_config_2026_02', 'handbook');