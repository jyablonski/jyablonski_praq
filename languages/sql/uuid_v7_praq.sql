-- needed for `gen_random_bytes` usage
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- OPTION A
-- Setup: Install extension for `uuid_generate_v7()` function
-- this has to be bundled into the image, an alternative is to create your own function
CREATE EXTENSION IF NOT EXISTS pg_uuidv7;

-- OPTION B
-- Pure SQL UUID v7 generator (no extension needed)
CREATE OR REPLACE FUNCTION uuid_generate_v7() RETURNS uuid AS $$
DECLARE
    unix_ms bigint;
    uuid_bytes bytea;
BEGIN
    unix_ms := (EXTRACT(EPOCH FROM clock_timestamp()) * 1000)::bigint;
    uuid_bytes := decode(lpad(to_hex(unix_ms), 12, '0'), 'hex') 
                  || gen_random_bytes(10);
    
    -- Set version (7) and variant (RFC 4122)
    uuid_bytes := set_byte(uuid_bytes, 6, (get_byte(uuid_bytes, 6) & 15) | 112);
    uuid_bytes := set_byte(uuid_bytes, 8, (get_byte(uuid_bytes, 8) & 63) | 128);
    
    RETURN encode(uuid_bytes, 'hex')::uuid;
END;
$$ LANGUAGE plpgsql VOLATILE;

drop table articles;
-- Create a table using UUID v7
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    title TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Insert some rows (IDs generated automatically)
INSERT INTO articles (title) VALUES 
    ('First Article'),
    ('Second Article'),
    ('Third Article');

-- See the sequential nature of the UUIDs
SELECT id, title FROM articles ORDER BY id;

/*
                  id                  |     title      
--------------------------------------+----------------
 019400a2-8b3c-7000-8123-4a5b6c7d8e9f | First Article
 019400a2-8b3d-7000-9234-5b6c7d8e9f0a | Second Article
 019400a2-8b3e-7000-a345-6c7d8e9f0a1b | Third Article
*/

-- The key insight: you can extract the timestamp from the UUID itself
-- First 48 bits are milliseconds since Unix epoch
SELECT 
    id,
    title,
    -- Extract timestamp from UUID v7
    to_timestamp(
        ('x' || lpad(replace(id::text, '-', ''), 12, '0'))::bit(48)::bigint / 1000.0
    ) AS id_timestamp,
    created_at
FROM articles;

-- Bonus: ordering by UUID = ordering by creation time
-- This query is efficient because it uses the PK index
SELECT * FROM articles 
WHERE id > '019400a2-8b3c-7000-0000-000000000000'
ORDER BY id
LIMIT 10;
