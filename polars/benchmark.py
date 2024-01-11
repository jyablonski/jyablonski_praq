import pandas as pd
import polars as pl
import numpy as np
import time

# Create a random DataFrame with a lot of data
n_rows = 2500000
n_cols = 40
df = pd.DataFrame(
    np.random.randn(n_rows, n_cols), columns=["col_{}".format(i) for i in range(n_cols)]
)
df_polars = pl.from_pandas(df)

# Benchmark Pandas
start_time = time.time()
df_merged = (
    df[df["col_0"] > 0]
    .groupby(["col_1", "col_2"])
    .mean()
    .sort_values(by=["col_3"], ascending=False)
    .merge(df.groupby(["col_1", "col_2"]).mean(), on=["col_1", "col_2"])
)
pandas_time = time.time() - start_time

# Benchmark Polars Rust
start_time = time.time()
df_merged_polars = (
    df_polars.filter(pl.col("col_0") > 0)
    .groupby(["col_1", "col_2"])
    .mean()
    .sort(by=["col_3"])
    .reverse()
    .join(df_polars.groupby(["col_1", "col_2"]).mean(), on=["col_1", "col_2"])
)
polars_time = time.time() - start_time

# Print results
print(f"Pandas 2.0 time: {pandas_time} seconds")
print(f"Polars Rust time: {polars_time}")
