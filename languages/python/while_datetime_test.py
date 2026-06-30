from datetime import datetime, timedelta
import time

date = datetime(2023, 12, 31).date()

while True and date > datetime(2023, 12, 28).date():
    print(date)
    time.sleep(5)
    date = date - timedelta(days=1)
