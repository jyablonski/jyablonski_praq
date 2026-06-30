import polars as pl

df1 = pl.DataFrame(
    {
        "id": [1, 2, 3, 4, 5],
        "color": ["red", "blue", "blue", "green", "green"],
        "price": [4.99, 3.99, 10.99, 99.99, 50.25],
    }
)

df2 = pl.DataFrame(
    {
        "id": [4, 100, 200, 300, 400],
        "color": ["green", "yellow", "green", "red", "purple"],
        "price": [99.99, 23.99, 110.99, 9.99, 450.25],
    }
)

df_unioned = pl.concat([df1, df2]).unique("id").sort("id")

df_color_avg_price_agg = df_unioned.group_by("color").agg([pl.mean("price")])
