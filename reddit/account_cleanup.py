import os
import time
from datetime import datetime, timedelta, timezone

import praw

CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
CLIENT_SECRET = os.environ["REDDIT_SECRET_KEY"]

username = os.environ["REDDIT_USER"]
password = os.environ["REDDIT_PASSWORD"]

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    username=username,
    password=password,
    user_agent=f"script:unblock-old:v1.0 (by /u/{username})",
)

print(f"Authenticated as /u/{reddit.user.me()}")

# Reddit's blocked listing returns each user with a `date` attribute:
# a UTC Unix timestamp of when the block was created.
cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).timestamp()

ok = failed = 0
for r in reddit.user.blocked():
    blocked_at = getattr(r, "date", None)
    if blocked_at is None or blocked_at >= cutoff:
        continue
    try:
        r.unblock()
        ok += 1
        when = datetime.fromtimestamp(blocked_at, tz=timezone.utc).strftime("%Y-%m-%d")
        print(f"Unblocked /u/{r}  (blocked {when})")
    except Exception as e:
        failed += 1
        print(f"Failed to unblock /u/{r}: {e}")
    time.sleep(1)  # be polite to the API

print(f"Done. Unblocked {ok}, failed {failed}.")
