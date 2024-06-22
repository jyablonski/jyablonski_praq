import pytest
from snowflake.snowpark.session import Session
import datetime
from snowflake.snowpark.mock import patch, ColumnEmulator, ColumnType
from snowflake.snowpark.functions import to_timestamp
from snowflake.snowpark.types import TimestampType


@patch(to_timestamp)
def mock_to_timestamp(column: ColumnEmulator, format=None) -> ColumnEmulator:
    ret_column = ColumnEmulator(
        data=[datetime.datetime.strptime(row, "%Y-%m-%dT%H:%M:%S%z") for row in column]
    )
    ret_column.sf_type = ColumnType(TimestampType(), True)
    return ret_column


# The call to pytest_addoption adds a command line option named snowflake-session to the pytest command. The
# Session fixture checks this command line option, and creates a local or live Session depending on its value.
# This allows you to easily switch between local and live modes for testing.


# `pytest --snowflake-session local`
# `pytest`
def pytest_addoption(parser):
    parser.addoption("--snowflake-session", action="store", default="live")


@pytest.fixture(scope="module")
def session() -> Session:
    return Session.builder.config("local_testing", True).create()


# commenting this out bc i have no snowflake account
# @pytest.fixture(scope='module')
# def session(request) -> Session:
#     if request.config.getoption('--snowflake-session') == 'local':
#         return Session.builder.config('local_testing', True).create()
#     else:
#         return Session.builder.configs(CONNECTION_PARAMETERS).create()
