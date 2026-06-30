from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, IntegerType
from pyiceberg.expressions import GreaterThanOrEqual

# this file is a pure python way of working with apache iceberg tables

# im not sold - you need to be able to have a ui where you can see
# the schema, the data, and the rest of the database
# https://py.iceberg.apache.org/configuration/
glue_database_name = "nba_elt_iceberg"
glue_catalog_uri = "s3://jyablonski2-iceberg"
my_namespace = "prod"

catalog = load_catalog("glue", **{"type": "glue"})

ns = catalog.list_namespaces()

tables = catalog.list_tables(glue_database_name)


pbp_data = catalog.load_table(f"{glue_database_name}.pbp_data")

# This returns a Table that represents an Iceberg table that can be queried and altered.
pbp_data


# schema evolution
with pbp_data.update_schema() as update:
    update.add_column("some_field", IntegerType(), "doc")

df = pbp_data.scan(
    row_filter=GreaterThanOrEqual("scoreaway", 100.0),
).to_pandas()

# no clue wtf you're supposed to do with this other than write it
# to s3 or something
df_arrow = pbp_data.scan(
    row_filter=GreaterThanOrEqual("scoreaway", 100.0),
).to_arrow()

# this is just very messy syntax.  you'd prboably just be using spark
# to do any of this instead
