from datetime import datetime
from collections import defaultdict


def count_user_sessions(logs: list[dict]) -> dict:
    user_visited_counter = {}

    for log_dict in logs:
        user_id = log_dict["user_id"]
        if user_id not in user_visited_counter:
            user_visited_counter[user_id] = 1
        else:
            user_visited_counter[user_id] += 1

    return user_visited_counter


logs = [
    {"user_id": 1, "timestamp": "2023-01-01 09:00:00"},
    {"user_id": 1, "timestamp": "2023-01-01 09:05:00"},
    {"user_id": 1, "timestamp": "2023-01-01 09:45:00"},
    {"user_id": 2, "timestamp": "2023-01-01 09:10:00"},
    {"user_id": 2, "timestamp": "2023-01-01 10:00:00"},
    {"user_id": 2, "timestamp": "2023-01-01 10:40:00"},
]

count_user_sessions(logs=logs)


def count_user_sessions(logs: list[dict]) -> dict:
    user_logs = defaultdict(list)
    for log in logs:
        user_logs[log["user_id"]].append(log["timestamp"])

    user_sessions = {}

    for user_id, user_timestamps in user_logs.items():
        timestamps = sorted(
            datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in user_timestamps
        )

        session_count = 1
        prev_ts = timestamps[0]

        for timestamp in timestamps[1:]:
            delta = (timestamp - prev_ts).total_seconds() / 60
            if delta > 30:
                session_count += 1
            prev_ts = timestamp

        user_sessions[user_id] = session_count

    return user_sessions


# a session is defined as any activity within a 30 minute time window
def count_user_sessions(logs: list[dict]) -> dict:
    from collections import defaultdict

    # Group logs by user
    user_logs = defaultdict(list)
    for log in logs:
        user_logs[log["user_id"]].append(log["timestamp"])

    user_sessions = {}

    for user_id, timestamps in user_logs.items():
        # Convert to datetime and sort
        timestamps = sorted(
            datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in timestamps
        )

        session_count = 1  # start with 1 session
        prev_ts = timestamps[0]

        for curr_ts in timestamps[1:]:
            delta = (curr_ts - prev_ts).total_seconds() / 60
            if delta > 30:
                session_count += 1
            prev_ts = curr_ts  # update last timestamp

        user_sessions[user_id] = session_count

    return user_sessions
