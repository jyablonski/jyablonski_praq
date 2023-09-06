from datetime import datetime, timedelta

import pandas as pd
import numpy as np

df = pd.DataFrame(
    data={
        "id": [1, 2, 3, 4, 5],
        "sales": [100, 200, 300, 0, 700],
        "is_valid": [True, True, False, False, True],
    }
)

# set `viewable_status` to 'Approved' When `is_valid` is True,
# otherwise look at the sales column and reject any record that has a value of 0, and if it is not equal to 0 then set it to Needs Review
df["viewable_status"] = np.where(
    df["is_valid"] == True,
    "Approved",
    np.where(df["sales"] == 0, "Rejected", "Needs Review"),
)
