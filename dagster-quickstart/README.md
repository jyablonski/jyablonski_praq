# Dagster

``` sh
uvx -U create-dagster project dagster-quickstart
uv add pandas

# generates an asset file
dg scaffold defs dagster.asset assets.py

dg list defs

# http://localhost:3000/locations/dagster-quickstart/asset-groups/default
dg dev
```

## Assets

Assets represent logical units of data such as a table, dataset, or ML model. Assets can have dependencies on other assets, forming a data lineage for your pipelines.

- They're defined with the `@dg.asset` decorator