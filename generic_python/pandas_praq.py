from datetime import datetime
import os

from faker import Faker
from faker.providers import internet
import numpy as np
import pandas as pd

fake = Faker()


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


df = make_fake_data(10000)

# case when statement
df["job_status"] = np.where(
    df["status"] == "Full Time",
    "Full Time",
    np.where(
        df["status"] == "Part Time",
        "Part Time",
        np.where(df["status"] == "Per Diem", "Part Time", "???"),
    ),
)

# query w/ multiple clauses
df2 = df.query(
    'salary >= 100000 | status == "Full Time" | full_name.str.contains("Heidi")'
).copy()

# aggregate column added to existing dataframe of records
df2["salary_agg"] = df2.groupby(["status"])["salary"].transform("mean")

# creating new dataframe of only the aggregate values
df2_agg = df2.groupby("status").agg({"salary": "mean"})

df3 = df2.query('status.isin(["Full Time", "Part Time"])')

df3["status"].unique()
