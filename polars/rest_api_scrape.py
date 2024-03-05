from datetime import datetime, timezone
import hashlib

# d = hashlib.md5("jacob".encode("utf-8")).hexdigest()

import polars as pl
import requests


api = "https://api.jyablonski.dev"
game_types_request = requests.get(f"{api}/game_types")
game_types = pl.DataFrame(game_types_request.json())

game_types_filtered = (
    game_types.filter(pl.col("n") >= 20)
    .select(
        "game_type",
        "season_type",
        "n",
        pl.col("n").sum().alias("total_count"),
    )
    .with_columns(
        game_type_hash=pl.col("game_type").hash(),
        created_at_utc=datetime.now(timezone.utc),
        created_at=datetime.now(),
        created_at_utcnow=datetime.utcnow(),
    )
)
game_types_filtered.dtypes
