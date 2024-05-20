from datetime import datetime, timedelta
import time

from faker import Faker
from faker.providers import internet

# small script to run any arbitrary function for a certain
# amount of time.
fake = Faker()
fake.add_provider(internet)


def generate_message(faker: Faker) -> dict[str, str]:
    return {
        "name": faker.name(),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "address": faker.address(),
    }


if __name__ == "__main__":
    start_time = datetime.now()
    time_difference = start_time + timedelta(hours=1)
    print(f"Starting at {start_time}, ending at {time_difference}")

    while True and datetime.now() < time_difference:
        message = generate_message(fake)
        print(message)
        time.sleep(5)
