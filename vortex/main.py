import polars as pl
import vortex as vx
import pyarrow.parquet as pq

# vortex files can work with duckdb, polars, ray etc through pyarrow
source_file_name = "../sql/tables/2025/marts/feature_flags_audit-2025-07-26.parquet"
vortex_file_name = "example.vortex"

vx_df = vx.array(pq.read_table(source_file_name))
vx.io.write(vx_df, vortex_file_name)

ds = vx.open(vortex_file_name).to_dataset()
df_pl = pl.scan_pyarrow_dataset(ds)


df = pl.read_parquet(source_file_name)
