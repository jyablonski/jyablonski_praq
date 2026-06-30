from datetime import datetime

import pandas as pd

if __name__ == "__main__":
    print("Starting ...")
    run_date = datetime.now()

    data = {"id": [1, 2, 3], "run_date": [run_date, run_date, run_date]}
    df = pd.DataFrame(data=data)
    print(df.head())
    print("Exiting ...")
