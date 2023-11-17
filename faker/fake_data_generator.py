from datetime import datetime
import importlib
import random
import time

from faker import Faker
import pandas as pd


class FakeDataGenerator:
    def __init__(
        self,
        faker=Faker(),
        faker_plugins: list[str] | None = None,
    ):
        self.faker = faker
        self.faker_plugins = faker_plugins

        if faker_plugins is not None:
            for plugin in self.faker_plugins:
                module_name = f"faker.providers.{plugin}"
                faker_module = importlib.import_module(module_name)

                self.faker.add_provider(faker_module)

    def _generate_value(self, col_config: dict[str]) -> str | None:
        faker_type = col_config.get("faker_type")
        faker_extras = col_config.get("faker_type_kwargs")
        random_choice_list = col_config.get("random_choice_list")

        if faker_type is not None:
            # this allows us to take the faker obj and pass
            # in the faker type str to it as an attribute
            # like self.faker.name

            # we can then return it as a method
            faker_method = getattr(self.faker, faker_type)

            if faker_extras is not None:
                # this gets passed like
                # `faker_method("start_date": "-3y", "end_date": "today")`
                return faker_method(**faker_extras)
            else:
                return faker_method()

        if random_choice_list is not None:
            return random.choice(random_choice_list)
        else:
            return None

    def generate_data(self, data_spec: list[dict], n=1000) -> pd.DataFrame:
        rows_data = [
            {
                col["column_name"]: self._generate_value(col_config=col)
                for col in data_spec
            }
            for _ in range(n)
        ]

        df = pd.DataFrame(rows_data)

        df["id"] = range(1, n + 1)
        df = pd.concat([df["id"], df.drop("id", axis=1)], axis=1)

        return df


fake_data_spec = [
    {"column_name": "person", "faker_type": "name"},
    {"column_name": "email", "faker_type": "email"},
    {"column_name": "company", "faker_type": "company"},
    {"column_name": "person_dob", "faker_type": "date_of_birth"},
    {
        "column_name": "signup_date",
        "faker_type": "date_between",
        "faker_type_kwargs": {"start_date": "-3y", "end_date": "today"},
    },
    {
        "column_name": "expiration_date",
        "faker_type": "date_between",
        "faker_type_kwargs": {"start_date": "-2y", "end_date": datetime(2026, 12, 31)},
    },
    {
        "column_name": "ip_address",
        "faker_type": "ipv4_private",
    },
    {
        "column_name": "fave_color",
        "faker_type": "color_name",
    },
    {
        "column_name": "employment_status",
        "faker_type": None,
        "random_choice_list": ["Salaried", "Contract", "Unemployed"],
    },
    # {
    #     "column_name": "salary",
    #     "faker_type": None,
    #     "dollar_distribution": int(round(random.uniform(50000, 150000), 0)),
    # },
]

int(round(random.uniform(50000, 150000), 0))
s = FakeDataGenerator()
# s = FakeDataGenerator(faker_plugins=["internet"])

s.faker.name()

# 15.57 seconds
# Your code snippet with timing
start_time = time.time()
df = s.generate_data(data_spec=fake_data_spec, n=100000)

end_time = time.time()
execution_time = end_time - start_time

# 43.5 seconds w/ the random uniform etc
