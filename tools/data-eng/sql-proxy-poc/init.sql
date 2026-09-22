CREATE TABLE connection_checks (
    id BIGSERIAL PRIMARY KEY,
    service_name TEXT NOT NULL,
    connection_mode TEXT NOT NULL,
    configured_target TEXT NOT NULL,
    client_host TEXT NOT NULL,
    backend_host TEXT NOT NULL,
    backend_port INTEGER NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
