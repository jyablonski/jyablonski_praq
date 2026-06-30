import os
import logging

import structlog

# https://betterstack.com/community/guides/logging/structlog/
# structlog is a Python library for structured logging, which outputs logs in a
# format that is easy for both humans and machines to parse, such as JSON.

# this enables logs to be easily ingested to services like Elasticsearch, Splunk,
# or Datadog for searching, filtering, and visualizations.

# works great with ELK stack. The way it works is that you have local log shippers
# like Filebeat that parse your log files and forward the log entries to your
# Logstash server. Logstash parses the log entries and stores them in Elasticsearch.
# Finally, you can view and search them in Kibana.


def set_app_vars(_, __, event_dict):
    event_dict["application"] = (
        f"rest-api-{os.environ.get(key='ENV_TYPE', default='dev')}"
    )
    event_dict["version"] = "1.0.0"
    return event_dict


structlog.configure(
    processors=[
        set_app_vars,
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        # structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        # this will give normal logging functionality in the console, but not json
        # structlog.dev.ConsoleRenderer(),
        # this will return logs as dictionaries
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)
logger = structlog.get_logger()


logger.info("hello world info", user="jyablonski")
logger.warning("hello world warning")
logger.critical("hello world critical")
logger.error("hello world error")

logger.info("user_logged_in", user_id=123, session_id="abc123")

x = 5
my_username = "jyablonski"


def user_login(username: str) -> None:
    if username == "jyablonski":
        raise Exception("User is banned")
    else:
        logger.info("User {username} logged in", username=username)


try:
    user_login(username=my_username)
except Exception:
    logger.error("An exception occurred", username=my_username, exc_info=True)
