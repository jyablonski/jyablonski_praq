import json
import os

import requests


def write_to_slack(error: str, webhook_url: str = os.environ.get("WEBHOOK_URL")):
    try:
        requests.post(
            webhook_url,
            data=json.dumps({"text": f"My Slack Message, {error}"}),
            headers={"Content-Type": "application/json"},
        )
    except BaseException as e:
        raise e


write_to_slack(error="hello_world")
