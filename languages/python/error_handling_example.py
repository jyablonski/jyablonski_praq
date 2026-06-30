from datetime import datetime


def count_str(s: str) -> int:
    count = 0

    if not isinstance(s, str):
        raise TypeError("Please Input a String Value")

    for i in s:
        if i == "!":
            raise ValueError("Pleaseeee don't use exclamations dude")
        count += 1

    try:
        count_dict = {"value": count}
        count_dict["test"]
    except KeyError as e:
        print(f"{e} Key doesn't exist but it's all good")
    finally:
        count_dict["created_at"] = datetime.now()
        print("finally block always runs!")

    return count_dict


count_str("helloo")
count_str("hell!o")
count_str(s=True)
