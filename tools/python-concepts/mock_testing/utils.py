import requests


def get_game_types() -> list[dict[str, str]]:
    url = "https://api.jyablonski.dev/game_typeszxczx"

    try:
        df = requests.get(url=url).json()
    except requests.JSONDecodeError:
        raise

    print(f"got {len(df)} records back")
    return df
