import pandas as pd
from snowflake.snowpark import Session
from snowflake.snowpark.types import (
    LongType,
    StructType,
    StructField,
    IntegerType,
    BooleanType,
    StringType,
    DoubleType,
)


session = Session.builder.config("local_testing", True).create()

df = session.create_dataframe([[1, 2], [3, 4]], ["a", "b"])
df.with_column("c", df["a"] + df["b"]).show()

# parse file data
session.file.put("snowflake/data.csv", "@mystage", auto_compress=False)
schema = StructType(
    [
        StructField("col1", IntegerType()),
        StructField("col2", StringType()),
        StructField("col3", BooleanType()),
        StructField("col4", DoubleType()),
    ]
)

# with option SKIP_HEADER set to 1, the header will be skipped when the csv file is loaded
dataframe = (
    session.read.schema(schema).option("SKIP_HEADER", 1).csv("@mystage/data.csv")
)
dataframe.show()


# parse pandas data

pandas_df = pd.DataFrame(
    data={
        "col1": pd.Series(["value1", "value2"]),
        "col2": pd.Series([1.23, 4.56]),
        "col3": pd.Series([123, 456]),
        "col4": pd.Series([True, False]),
    }
)

dataframe = session.create_dataframe(data=pandas_df)
dataframe.show()


dataframe = session.create_dataframe(
    data=[
        ["value1", 1.23, 123, True],
        ["value2", 4.56, 456, False],
    ],
    schema=StructType(
        [
            StructField("col1", StringType()),
            StructField("col2", DoubleType()),
            StructField("col3", LongType()),
            StructField("col4", BooleanType()),
        ]
    ),
)

pandas_dataframe = dataframe.to_pandas()
print(pandas_dataframe.to_string())
