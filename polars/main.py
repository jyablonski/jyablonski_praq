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
df_filtered = df[df["col_0"] > 0]
df_grouped = df.groupby(["col_1", "col_2"]).mean()
df_sorted = df.sort_values(by=["col_3"], ascending=False)
df_merged = pd.merge(df, df_grouped, on=["col_1", "col_2"])
pandas_time = time.time() - start_time

# Benchmark Polars Rust
start_time = time.time()
df_filtered_polars = df_polars.filter(pl.col("col_0") > 0)
df_grouped_polars = df_polars.groupby(["col_1", "col_2"]).mean()
df_sorted_polars = df_polars.sort(by=["col_3"]).reverse()
df_merged_polars = df_polars.join(df_grouped_polars, on=["col_1", "col_2"])
polars_time = time.time() - start_time

# Print results
print(f"Pandas 2.0 time: {pandas_time} seconds")
print(f"Polars Rust time: {polars_time}")
