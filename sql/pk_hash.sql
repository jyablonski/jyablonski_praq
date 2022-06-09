MD5(player::text) as md5_player,              /* ::text works here */
SHA256(player::bytea)::text as sha256_player,
SHA512(player::bytea)::text as sha512_player, /* bytea needed; ::text wont work */
{{ dbt_utils.hash('player') }}as player_hash, /* this is just MD5, so it's the same as md5_player */
{{ dbt_utils.surrogate_key(['player', 'date']) }} as player_pk,