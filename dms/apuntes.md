# DMS
[AWS Doc 1](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Reference.DataTypes.html)

[AWS Doc 2](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TableMapping.SelectionTransformation.Transformations.html)

## Postgres
Postgres Enum Value Types are lost in the Migration, they just land as `varchar(255)`.  

``` sql
CREATE TYPE jacob_enum AS ENUM ('sad', 'ok', 'happy');

CREATE TABLE public.jacob_test (
    id serial,
    name text,
    is_deleted boolean,
    is_active boolean default false,
    current_mood jacob_enum,
    created_at timestamp default now()
);


insert into public.jacob_test (name, is_deleted, is_active, current_mood)
values ('jacob', false, true, 'happy'),
       ('big otis', true, false, 'sad'),
       ('testaroo', false, false, 'ok');
       
select *
from public.jacob_test;
```

## MySQL
Have to set 3 things:
- Turn the `id` columns from `INT` to `AUTO_INCREMENT`
- Set a Default Value on the Timestamp Columns
- Turn the Enum Columns back into Enums instead of `varchar(255)`

``` sql
ALTER TABLE jacob_db.DMS_jacob_test
MODIFY COLUMN id INT AUTO_INCREMENT PRIMARY KEY;

ALTER TABLE jacob_db.DMS_jacob_test
MODIFY COLUMN created_at datetime(6) DEFAULT CURRENT_TIMESTAMP(6);

ALTER TABLE jacob_db.DMS_jacob_test
MODIFY COLUMN current_mood ENUM('sad', 'ok', 'happy');

select *
from jacob_db.DMS_jacob_test;

insert into jacob_db.DMS_jacob_test (name, is_deleted, is_active, current_mood)
values ('test_v3', 0, 1, 'happy');

```
Also will have to manually set indexes on the Tables, either manually or via Liquibase.  These are low row count though so I'm not as concerned with that.

## DMS Mapping
Mapping Rules which perform the following functions:
1. Selects only the `jacob_test` Table in the `public` Schema in the Source PostgreSQL Database
2. Adds a Table Name prefix `DMS_` so that it appears like `DMS_jacob_test` in MySQL
3. Specifies to change the data type of the `is_deleted` Column on `jacob_test` to a Boolean during the Migration
   1. Without this, it lands in MySQL as a `varchar(5)`
4. Specifies to change the data type of the `is_active` Column on `jacob_test` to a Boolean during the Migration
5. Specifies the landing Schema in MySQL to be `jacob_db` for every table in the Migration

``` json
{
	"rules": [
		{
			"rule-type": "selection",
			"rule-id": "1",
			"rule-name": "1",
			"object-locator": {
				"schema-name": "public",
				"table-name": "jacob_test"
			},
			"rule-action": "include"
		},
		{
			"rule-type": "transformation",
			"rule-id": "2",
			"rule-name": "2",
			"rule-action": "add-prefix",
			"rule-target": "table",
			"object-locator": {
				"schema-name": "public",
				"table-name": "jacob_test"
			},
			"value": "DMS_"
		},
        {
            "rule-type": "transformation",
            "rule-id": "3",
            "rule-name": "3",
            "rule-action": "change-data-type",
            "rule-target": "column",
            "object-locator": {
                "schema-name": "public",
                "table-name": "jacob_test",
                "column-name": "is_deleted"
            },
            "data-type": {
                "type": "boolean"
            }
        },
        {
            "rule-type": "transformation",
            "rule-id": "4",
            "rule-name": "4",
            "rule-action": "change-data-type",
            "rule-target": "column",
            "object-locator": {
                "schema-name": "public",
                "table-name": "jacob_test",
                "column-name": "is_active"
            },
            "data-type": {
                "type": "boolean"
            }
        },
        {
            "rule-type": "transformation",
            "rule-id": "5",
            "rule-name": "5",
            "rule-action": "rename",
            "rule-target": "schema",
            "object-locator": {
                "schema-name": "public"
            },
            "value": "jacob_db"
        }
	]
}
```
