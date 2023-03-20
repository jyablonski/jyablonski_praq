import awswrangler as wr
from faker import Faker
from faker.providers import internet
import numpy as np
import pandas as pd

# to do multi line editing do
# CRTL + F
# ALT + ENTER


fake = Faker()
fake.add_provider(internet)

# example of what can be provided
fake.profile()

print(fake.name())
print(fake.address())
print(fake.text())
print(fake.ipv4_private())
print(fake.user_name())
print(fake.date_of_birth())
print(fake.ssn())
print(fake.phone_number())
print(fake.credit_card_number())
print(fake.company())
print(fake.company_email())


def make_fake_data(num: int = 5000) -> pd.DataFrame():
    # lists to randomly assign to workers
    status_list = ["Full Time", "Part Time", "Per Diem"]
    team_list = [fake.color_name() for x in range(10)]

    df = [
        {
            "id": x,
            "full_name": fake.name(),
            "email": fake.email(),
            "hire_date": fake.date_between(start_date="-3y", end_date="today"),
            "status": np.random.choice(
                status_list, p=[0.50, 0.30, 0.20]
            ),  # assign items from list with different probabilities
            "fav_color": np.random.choice(team_list),
            "salary": int(round(np.random.uniform(50000, 150000) / 500, 0) * 500),
        }
        for x in range(num)
    ]

    df = pd.DataFrame(df)
    return df


worker_df = make_fake_data(100000)
worker_df.head()
