# https://prepare.sh/engineering/de/amazon/
import pandas as pd


data = pd.DataFrame(
    data={
        "product_id": [1, 2, 3, 4, 5],
        "product_name": ["A", "B", "C", "D", "E"],
        "price_per_unit": [10, 20, 30, 40, 50],
        "quantity_sold": [100, 200, 300, 400, 500],
        "date": ["2020-01-01", "2022-01-02", "2022-01-03", "2022-01-04", "2024-01-05"],
    }
)

data["date"] = pd.to_datetime(data["date"])

data_clean = data.query('date >= "2022-01-01" and date < "2023-01-01"')
data_clean["total_revenue"] = data_clean["price_per_unit"] * data_clean["quantity_sold"]

max_revenue_product = data_clean.max()["total_revenue"]


l1 = [1, 2, 4]
l2 = [1, 3, 4]

merged_list = sorted(l1 + l2)


def reverse_string(s: str) -> list[str]:
    return list(s[::-1])
