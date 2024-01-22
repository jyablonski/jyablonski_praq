[Article](https://jove.medium.com/build-a-meltano-target-within-1-hour-7134df6244fb)

``` sh
pip install meltano

# add an extractor
# this will add the plugin to the `meltano.yml` file
meltano add extractor tap-github --variant=meltanolabs

# invoke it to see if it worked
meltano invoke tap-github --help

meltano config tap-github set --interactive

meltano select tap-github --list

meltano add loader target-jsonl --variant=andyh1203

meltano run tap-github target-jsonl

docker run --name meltano_postgres -p 5432:5432 -e POSTGRES_USER=meltano -e POSTGRES_PASSWORD=password -d postgres

meltano add loader target-postgres --variant=meltanolabs

meltano invoke target-postgres --help

meltano config target-postgres list

meltano config target-postgres

meltano --environment=dev run tap-github target-postgres
```