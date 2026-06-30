-- Sequence-exhaustion audit using ONLY catalog metadata + the sequence
-- relations themselves. No max(id), no user-table reads, no full scans.
-- Requires Postgres 10+ (pg_sequences view, identity columns).
--
-- Current position comes from pg_sequences.last_value, which is:
--   * a single-page read of the tiny sequence relation (not a table scan)
--   * NULL if the sequence has never been called yet, or if the current
--     user lacks USAGE/SELECT on it (graceful -- no error, no abort)

WITH seq_links AS (
    -- (a) sequences OWNED by a column: serial (deptype 'a') + identity ('i')
    SELECT
        d.objid       AS seq_oid,
        d.refobjid    AS table_oid,
        d.refobjsubid AS column_attnum
    FROM pg_depend d
    JOIN pg_class s
        ON s.oid = d.objid
       AND s.relkind = 'S'
    WHERE d.classid    = 'pg_class'::regclass
      AND d.refclassid = 'pg_class'::regclass
      AND d.deptype IN ('a', 'i')
      AND d.refobjsubid > 0

    UNION

    -- (b) sequences referenced by a column DEFAULT nextval(...), including
    --     ones NOT formally OWNED BY the column. The default's pg_attrdef
    --     object has a normal ('n') dependency on the sequence -- so we link
    --     through that instead of parsing the expression text.
    SELECT
        d.refobjid AS seq_oid,
        ad.adrelid AS table_oid,
        ad.adnum   AS column_attnum
    FROM pg_depend d
    JOIN pg_attrdef ad
        ON ad.oid = d.objid
    JOIN pg_class s
        ON s.oid = d.refobjid
       AND s.relkind = 'S'
    WHERE d.classid    = 'pg_attrdef'::regclass
      AND d.refclassid = 'pg_class'::regclass
      AND d.deptype = 'n'
),

links AS (
    SELECT DISTINCT seq_oid, table_oid, column_attnum
    FROM seq_links
),

resolved AS (
    SELECT
        tbl_ns.nspname AS table_schema,
        tbl.relname    AS table_name,
        att.attname    AS column_name,
        format_type(att.atttypid, att.atttypmod) AS data_type,
        CASE
            WHEN att.attidentity <> '' THEN 'identity'
            ELSE 'serial/default nextval'
        END AS autoincrement_type,
        seq_ns.nspname || '.' || seq.relname AS sequence_name,
        ps.last_value,
        ps.max_value AS sequence_max_value,
        ps.cycle     AS sequence_cycles,
        CASE att.atttypid
            WHEN 'pg_catalog.int2'::regtype THEN 32767::numeric
            WHEN 'pg_catalog.int4'::regtype THEN 2147483647::numeric
            WHEN 'pg_catalog.int8'::regtype THEN 9223372036854775807::numeric
        END AS type_limit
    FROM links l
    JOIN pg_class seq        ON seq.oid = l.seq_oid
    JOIN pg_namespace seq_ns ON seq_ns.oid = seq.relnamespace
    JOIN pg_class tbl        ON tbl.oid = l.table_oid
    JOIN pg_namespace tbl_ns ON tbl_ns.oid = tbl.relnamespace
    JOIN pg_attribute att
        ON att.attrelid = l.table_oid
       AND att.attnum   = l.column_attnum
       AND NOT att.attisdropped
    LEFT JOIN pg_sequences ps
        ON ps.schemaname   = seq_ns.nspname
       AND ps.sequencename = seq.relname
    WHERE seq_ns.nspname NOT IN ('pg_catalog', 'information_schema')
      AND att.atttypid IN (
          'pg_catalog.int2'::regtype,
          'pg_catalog.int4'::regtype,
          'pg_catalog.int8'::regtype
      )
)

SELECT
    table_schema,
    table_name,
    column_name,
    data_type,
    autoincrement_type,
    sequence_name,
    last_value,
    sequence_max_value,
    type_limit,
    -- the true wall: whichever the sequence hits first
    LEAST(COALESCE(sequence_max_value, type_limit), type_limit) AS effective_limit,
    round(
        (last_value::numeric
            / LEAST(COALESCE(sequence_max_value, type_limit), type_limit)) * 100,
        4
    ) AS pct_of_limit,
    LEAST(COALESCE(sequence_max_value, type_limit), type_limit)
        - last_value AS remaining_values,
    sequence_cycles,
    CASE
        WHEN last_value IS NULL THEN 'unknown (never called or no privilege)'
        WHEN last_value >= LEAST(COALESCE(sequence_max_value, type_limit), type_limit) * 0.95 THEN 'critical'
        WHEN last_value >= LEAST(COALESCE(sequence_max_value, type_limit), type_limit) * 0.80 THEN 'high'
        WHEN last_value >= LEAST(COALESCE(sequence_max_value, type_limit), type_limit) * 0.50 THEN 'medium'
        ELSE 'low'
    END AS risk_level
FROM resolved
ORDER BY
    pct_of_limit DESC NULLS LAST,
    last_value   DESC NULLS LAST;