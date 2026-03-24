"""Table DDL definitions for user_analytics."""

TABLE_NAME = "user_analytics"
STAGING_TABLE_NAME = "user_analytics_staging"


def get_columns() -> list[tuple[str, str]]:
    """Return (column_name, column_type) pairs for user_analytics."""
    return [
        ("user_id", "BIGINT"),
        # Integer counts
        ("page_views", "INTEGER NOT NULL DEFAULT 0"),
        ("sessions", "INTEGER NOT NULL DEFAULT 0"),
        ("email_opens", "INTEGER NOT NULL DEFAULT 0"),
        ("email_clicks", "INTEGER NOT NULL DEFAULT 0"),
        ("push_sends", "INTEGER NOT NULL DEFAULT 0"),
        # Float scores
        ("engagement_score", "DOUBLE PRECISION"),
        ("churn_risk", "DOUBLE PRECISION"),
        ("lifetime_value", "DOUBLE PRECISION"),
        ("open_rate", "DOUBLE PRECISION"),
        ("click_rate", "DOUBLE PRECISION"),
        # Varchar segments
        ("audience_segment", "VARCHAR(50)"),
        ("lifecycle_stage", "VARCHAR(50)"),
        ("acquisition_source", "VARCHAR(50)"),
        ("preferred_platform", "VARCHAR(50)"),
        ("content_affinity", "VARCHAR(50)"),
        # Boolean flags
        ("is_subscriber", "BOOLEAN NOT NULL DEFAULT FALSE"),
        ("is_active", "BOOLEAN NOT NULL DEFAULT FALSE"),
        ("has_mobile_app", "BOOLEAN NOT NULL DEFAULT FALSE"),
        # Timestamps
        ("last_seen_at", "TIMESTAMP WITH TIME ZONE"),
        ("last_email_at", "TIMESTAMP WITH TIME ZONE"),
    ]


def create_table(conn, table_name: str) -> None:
    """Create a user_analytics table (or staging variant)."""
    columns = get_columns()
    col_defs = ", ".join(f"{name} {dtype}" for name, dtype in columns)
    conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs}, PRIMARY KEY (user_id))"
    )


def drop_table(conn, table_name: str) -> None:
    """Drop a table if it exists."""
    conn.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
