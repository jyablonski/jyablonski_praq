import os
import pytest
import pytest_mock
import sqlite3
import pandas as pd
import numpy as np
import boto3
from moto import mock_s3
from datetime import datetime, timedelta
from ..main import get_player_stats_transform
from ..utils import *


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


# this creates an s3 client where u can create a bucket and then test with.
@pytest.fixture(scope="function")
def s3(aws_credentials):
    with mock_s3():
        yield boto3.client("s3", region_name="us-east-1")


class MyModel(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def save(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.put_object(Bucket="mybucket", Key=self.name, Body=self.value)


@pytest.fixture
def setup_database():
    """Fixture to set up an empty in-memory database"""
    conn = sqlite3.connect(":memory:")
    yield conn


# @pytest.fixture
# def s3_data():
#     with mock_s3():
#         conn = boto3.resource('s3', region_name='us-east-1')
#         # We need to create the bucket since this is all in Moto's 'virtual' AWS account
#         conn.create_bucket(Bucket='mybucket')
#         model_instance = MyModel('jacob', 'is awesome')
#         model_instance.save()
#         body = conn.Object('mybucket', 'steve').get()['Body'].read().decode("utf-8")
#         return body

# @pytest.fixture(scope='session')
# def db_connection(docker_services, docker_ip):
#     """
#     :param docker_services: pytest-docker plugin fixture
#     :param docker_ip: pytest-docker plugin fixture
#     :return: psycopg2 connection class
#     """
#     db_settings = {
#         'database'        : 'test_database',
#         'user'            : 'test',
#         'host'            : 'test',
#         'password'        : 'password',
#         'port'            : 5432,
#         'application_name': 'test_app'
#     }
#     dbc = psycopg2.connect(**db_settings)
#     dbc.autocommit = True
#     return dbc


# @pytest.fixture(autouse=True)
# def _mock_db_connection(mocker, db_connection):
#     """
#     This will alter application database connection settings, once and for all the tests
#     in unit tests module.
#     :param mocker: pytest-mock plugin fixture
#     :param db_connection: connection class
#     :return: True upon successful monkey-patching
#     """
#     mocker.patch('db.database.dbc', db_connection)
#     return True

# @pytest.fixture(scope='session')
# def contracts_data():
#     """
#     Fixture to load contracts data from a csv file for testing.
#     """
#     fname = os.path.join(os.path.dirname(__file__), 'tests/fixture_csvs/contracts_data.csv')
#     # df = pd.read_csv('/fixture_csvs/contracts.csv')
#     df = pd.read_csv(fname)
#     df = df.rename(columns={df.columns[3]: 'team', df.columns[4]: 'season_salary'})
#     df = df[['Player', 'team', 'season_salary']]
#     df.columns = df.columns.str.lower()
#     df = df.drop_duplicates()
#     df = df.query('season_salary != "Salary" & season_salary != "2021-22"').reset_index()
#     df['season_salary'] = df['season_salary'].str.replace(',', "", regex = True)
#     df['season_salary'] = df['season_salary'].str.replace('$', "", regex = True)
#     df['team'] = df['team'].str.replace("PHO", "PHX")
#     df['team'] = df['team'].str.replace("CHO", "CHA")
#     df['team'] = df['team'].str.replace("BRK", "BKN")
#     df['season_salary'] = pd.to_numeric(df['season_salary'])
#     df['player'] = df['player'].str.normalize('NFKD').str.encode('ascii', errors = 'ignore').str.decode('utf-8')
#     df = df.reset_index(drop = True)
#     return df


@pytest.fixture(scope="session")
def player_stats_data():
    """
    Fixture to load player stats data from a csv file for testing.
    """
    fname = os.path.join(
        os.path.dirname(__file__), "tests/fixture_csvs/player_stats_data.csv"
    )
    stats = pd.read_csv(fname)
    stats["PTS"] = pd.to_numeric(stats["PTS"])

    stats = stats.query("Player == Player").reset_index()
    stats["Player"] = (
        stats["Player"]
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    stats.columns = stats.columns.str.lower()
    stats["scrape_date"] = datetime.now().date()
    stats = stats.drop("index", axis=1)
    return stats


@pytest.fixture(scope="session")
def boxscores_data():
    """
    Fixture to load boxscores data from a csv file for testing.
    """
    fname = os.path.join(
        os.path.dirname(__file__), "tests/fixture_csvs/boxscores_data.csv"
    )
    df = pd.read_csv(fname)
    day = (datetime.now() - timedelta(1)).day
    month = (datetime.now() - timedelta(1)).month
    year = (datetime.now() - timedelta(1)).year
    season_type = "Regular Season"
    df[
        [
            "FGM",
            "FGA",
            "FGPercent",
            "threePFGMade",
            "threePAttempted",
            "threePointPercent",
            "OREB",
            "DREB",
            "TRB",
            "AST",
            "STL",
            "BLK",
            "TOV",
            "PF",
            "PTS",
            "PlusMinus",
            "GmSc",
        ]
    ] = df[
        [
            "FGM",
            "FGA",
            "FGPercent",
            "threePFGMade",
            "threePAttempted",
            "threePointPercent",
            "OREB",
            "DREB",
            "TRB",
            "AST",
            "STL",
            "BLK",
            "TOV",
            "PF",
            "PTS",
            "PlusMinus",
            "GmSc",
        ]
    ].apply(
        pd.to_numeric
    )
    df["date"] = str(year) + "-" + str(month) + "-" + str(day)
    df["date"] = pd.to_datetime(df["date"])
    df["Type"] = season_type
    df["Season"] = 2022
    df["Location"] = df["Location"].apply(lambda x: "A" if x == "@" else "H")
    df["Team"] = df["Team"].str.replace("PHO", "PHX")
    df["Team"] = df["Team"].str.replace("CHO", "CHA")
    df["Team"] = df["Team"].str.replace("BRK", "BKN")
    df["Opponent"] = df["Opponent"].str.replace("PHO", "PHX")
    df["Opponent"] = df["Opponent"].str.replace("CHO", "CHA")
    df["Opponent"] = df["Opponent"].str.replace("BRK", "BKN")
    df = df.query("Player == Player").reset_index(drop=True)
    df["Player"] = (
        df["Player"]
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    df.columns = df.columns.str.lower()
    return df


@pytest.fixture(scope="session")
def opp_stats_data():
    """
    Fixture to load team opponent stats data from a csv file for testing.
    """
    fname = os.path.join(
        os.path.dirname(__file__), "tests/fixture_csvs/opp_stats_data.csv"
    )
    df = pd.read_csv(fname)
    df = df[["Team", "FG%", "3P%", "3P", "PTS"]]
    df = df.rename(
        columns={
            df.columns[0]: "team",
            df.columns[1]: "fg_percent_opp",
            df.columns[2]: "threep_percent_opp",
            df.columns[3]: "threep_made_opp",
            df.columns[4]: "ppg_opp",
        }
    )
    df = df.query('team != "League Average"')
    df = df.reset_index(drop=True)
    df["scrape_date"] = datetime.now().date()
    return df


@pytest.fixture(scope="session")
def injuries_data():
    """
    Fixture to load injuries data from a csv file for testing.
    """
    fname = os.path.join(
        os.path.dirname(__file__), "tests/fixture_csvs/injuries_data.csv"
    )
    df = pd.read_csv(fname)
    df = df.rename(columns={"Update": "Date"})
    df.columns = df.columns.str.lower()
    df["scrape_date"] = datetime.now().date()
    return df


@pytest.fixture(scope="session")
def transactions_data():
    """
    Fixture to load transactions data from a csv file for testing.
    """
    fname = os.path.join(
        os.path.dirname(__file__), "tests/fixture_csvs/transactions_data.csv"
    )
    transactions = pd.read_csv(fname)
    transactions.columns = ["Date", "Transaction"]
    transactions = transactions.query(
        'Date == Date & Date != ""'
    ).reset_index()  # filters out nulls and empty values
    transactions = transactions.explode("Transaction")
    transactions["Date"] = transactions["Date"].str.replace(
        "?", "Jan 1, 2021", regex=True  # bad data 10-14-21
    )
    transactions["Date"] = pd.to_datetime(transactions["Date"])
    transactions.columns = transactions.columns.str.lower()
    transactions = transactions[["date", "transaction"]]
    transactions["scrape_date"] = datetime.now().date()
    return transactions


@pytest.fixture(scope="session")
def advanced_stats_data():
    """
    Fixture to load team advanced stats data from a csv file for testing.
    """
    fname = os.path.join(
        os.path.dirname(__file__), "tests/fixture_csvs/advanced_stats_data.csv"
    )
    df = pd.read_csv(fname)
    df.drop(columns=df.columns[0], axis=1, inplace=True)

    df.columns = [
        "Team",
        "Age",
        "W",
        "L",
        "PW",
        "PL",
        "MOV",
        "SOS",
        "SRS",
        "ORTG",
        "DRTG",
        "NRTG",
        "Pace",
        "FTr",
        "3PAr",
        "TS%",
        "bby1",  # the bby columns are because of hierarchical html formatting - they're just blank columns
        "eFG%",
        "TOV%",
        "ORB%",
        "FT/FGA",
        "bby2",
        "eFG%_opp",
        "TOV%_opp",
        "DRB%_opp",
        "FT/FGA_opp",
        "bby3",
        "Arena",
        "Attendance",
        "Att/Game",
    ]
    df.drop(["bby1", "bby2", "bby3"], axis=1, inplace=True)
    df = df.query('Team != "League Average"').reset_index()
    # Playoff teams get a * next to them ??  fkn stupid, filter it out.
    df["Team"] = df["Team"].str.replace("*", "", regex=True)
    df["scrape_date"] = datetime.now().date()
    df.columns = df.columns.str.lower()
    return df


@pytest.fixture(scope="session")
def odds_data():
    """
    Fixture to load odds data from a csv file for testing.
    """
    fname = os.path.join(os.path.dirname(__file__), "tests/fixture_csvs/odds_data.csv")
    df = pd.read_csv(fname)
    day = (datetime.now() - timedelta(1)).day
    month = (datetime.now() - timedelta(1)).month
    year = (datetime.now() - timedelta(1)).year
    data1 = df[0].copy()
    date_try = str(year) + " " + data1.columns[0]
    data1["date"] = np.where(
        date_try == "2021 Today",
        datetime.now().date(),  # if the above is true, then return this
        str(year) + " " + data1.columns[0],  # if false then return this
    )
    # date_try = pd.to_datetime(date_try, errors="coerce", format="%Y %a %b %dth")
    date_try = data1["date"].iloc[0]
    data1.columns.values[0] = "Today"
    data1.reset_index(drop=True)
    data1["Today"] = data1["Today"].str.replace(
        "LA Clippers", "LAC Clippers", regex=True
    )
    data1["Today"] = data1["Today"].str.replace("AM", "AM ", regex=True)
    data1["Today"] = data1["Today"].str.replace("PM", "PM ", regex=True)
    data1["Time"] = data1["Today"].str.split().str[0]
    data1["datetime1"] = pd.to_datetime(
        date_try.strftime("%Y-%m-%d") + " " + data1["Time"]
    ) - timedelta(hours=5)

    data2 = df[1].copy()
    data2.columns.values[0] = "Today"
    data2.reset_index(drop=True)
    data2["Today"] = data2["Today"].str.replace(
        "LA Clippers", "LAC Clippers", regex=True
    )
    data2["Today"] = data2["Today"].str.replace("AM", "AM ", regex=True)
    data2["Today"] = data2["Today"].str.replace("PM", "PM ", regex=True)
    data2["Time"] = data2["Today"].str.split().str[0]
    data2["datetime1"] = (
        pd.to_datetime(date_try.strftime("%Y-%m-%d") + " " + data2["Time"])
        - timedelta(hours=5)
        + timedelta(days=1)
    )
    data2["date"] = data2["datetime1"].dt.date

    data = data1.append(data2).reset_index(drop=True)
    data["SPREAD"] = data["SPREAD"].str[:-4]
    data["TOTAL"] = data["TOTAL"].str[:-4]
    data["TOTAL"] = data["TOTAL"].str[2:]
    data["Today"] = data["Today"].str.split().str[1:2]
    data["Today"] = pd.DataFrame(
        [str(line).strip("[").strip("]").replace("'", "") for line in data["Today"]]
    )
    data["SPREAD"] = data["SPREAD"].str.replace("pk", "-1", regex=True)
    data["SPREAD"] = data["SPREAD"].str.replace("+", "", regex=True)
    data.columns = data.columns.str.lower()
    data = data[["today", "spread", "total", "moneyline", "date", "datetime1"]]
    data = data.rename(columns={data.columns[0]: "team"})
    data = data.query("date == date.min()")  # only grab games from upcoming day
    return data


# @pytest.fixture(scope='session')
# def pbp_data():
#     """
#     Fixture to load pbp data from a csv file for testing.
#     """
#     fname = os.path.join(os.path.dirname(__file__), 'tests/fixture_csvs/pbp_data.csv')
#     df = pd.read_csv(fname)
#     yesterday = datetime.now().date() - timedelta(1)
#     yesterday_hometeams = (
#         df.query('location == "H"')[["team"]].drop_duplicates().dropna()
#     )
#     yesterday_hometeams["team"] = yesterday_hometeams["team"].str.replace(
#         "PHX", "PHO"
#     )
#     yesterday_hometeams["team"] = yesterday_hometeams["team"].str.replace(
#         "CHA", "CHO"
#     )
#     yesterday_hometeams["team"] = yesterday_hometeams["team"].str.replace(
#         "BKN", "BRK"
#     )

#     away_teams = (
#         df.query('location == "A"')[["team", "opponent"]].drop_duplicates().dropna()
#     )
#     away_teams = away_teams.rename(
#         columns={
#             away_teams.columns[0]: "AwayTeam",
#             away_teams.columns[1]: "HomeTeam",
#         }
#     )
#     newdate = str(
#         df["date"].drop_duplicates()[0]
#     )  # this assumes all games in the boxscores df are 1 date
#     newdate = pd.to_datetime(newdate).strftime(
#         "%Y%m%d"
#     )  # formatting into url format.
#     pbp_list = pd.DataFrame()
#     for i in yesterday_hometeams["team"]:
#         url = "https://www.basketball-reference.com/boxscores/pbp/{}0{}.html".format(
#             newdate, i
#         )
#         df = pd.read_html(url)[0]
#         df.columns = df.columns.map("".join)
#         df = df.rename(
#             columns={
#                 df.columns[0]: "Time",
#                 df.columns[1]: "descriptionPlayVisitor",
#                 df.columns[2]: "AwayScore",
#                 df.columns[3]: "Score",
#                 df.columns[4]: "HomeScore",
#                 df.columns[5]: "descriptionPlayHome",
#             }
#         )
#         conditions = [
#             (
#                 df["HomeScore"].str.contains("Jump ball:", na=False)
#                 & df["Time"].str.contains("12:00.0")
#             ),
#             (df["HomeScore"].str.contains("Start of 2nd quarter", na=False)),
#             (df["HomeScore"].str.contains("Start of 3rd quarter", na=False)),
#             (df["HomeScore"].str.contains("Start of 4th quarter", na=False)),
#             (df["HomeScore"].str.contains("Start of 1st overtime", na=False)),
#             (df["HomeScore"].str.contains("Start of 2nd overtime", na=False)),
#             (df["HomeScore"].str.contains("Start of 3rd overtime", na=False)),
#             (
#                 df["HomeScore"].str.contains("Start of 4th overtime", na=False)
#             ),  # if more than 4 ots then rip
#         ]
#         values = [
#             "1st Quarter",
#             "2nd Quarter",
#             "3rd Quarter",
#             "4th Quarter",
#             "1st OT",
#             "2nd OT",
#             "3rd OT",
#             "4th OT",
#         ]
#         df["Quarter"] = np.select(conditions, values, default=None)
#         df["Quarter"] = df["Quarter"].fillna(method="ffill")
#         df = df.query(
#             'Time != "Time" & Time != "2nd Q" & Time != "3rd Q" & Time != "4th Q" & Time != "1st OT" & Time != "2nd OT" & Time != "3rd OT" & Time != "4th OT"'
#         ).copy()  # use COPY to get rid of the fucking goddamn warning bc we filtered stuf out
#         # anytime you filter out values w/o copying and run code like the lines below it'll throw a warning.
#         df["HomeTeam"] = i
#         df["HomeTeam"] = df["HomeTeam"].str.replace("PHO", "PHX")
#         df["HomeTeam"] = df["HomeTeam"].str.replace("CHO", "CHA")
#         df["HomeTeam"] = df["HomeTeam"].str.replace("BRK", "BKN")
#         df = df.merge(away_teams)
#         df[["scoreAway", "scoreHome"]] = df["Score"].str.split("-", expand=True)
#         df["scoreAway"] = pd.to_numeric(df["scoreAway"], errors="coerce")
#         df["scoreAway"] = df["scoreAway"].fillna(method="ffill")
#         df["scoreAway"] = df["scoreAway"].fillna(0)
#         df["scoreHome"] = pd.to_numeric(df["scoreHome"], errors="coerce")
#         df["scoreHome"] = df["scoreHome"].fillna(method="ffill")
#         df["scoreHome"] = df["scoreHome"].fillna(0)
#         df["marginScore"] = df["scoreHome"] - df["scoreAway"]
#         df["Date"] = yesterday
#         df = df.rename(
#             columns={
#                 df.columns[0]: "timeQuarter",
#                 df.columns[6]: "numberPeriod",
#             }
#         )
#         pbp_list = pbp_list.append(df)
#         df = pd.DataFrame()
#     pbp_list.columns = pbp_list.columns.str.lower()
#     pbp_list = pbp_list.query(
#         "(awayscore.notnull()) | (homescore.notnull())", engine="python"
#     )
#                 # filtering only scoring plays here, keep other all other rows in future for lineups stuff etc.
#     return pbp_list

# https://stackoverflow.com/questions/52973700/how-to-save-the-beautifulsoup-object-to-a-file-and-then-read-from-it-as-beautifu
## NEW TESTS
@pytest.fixture(scope="session")
def player_transformed_stats_data_raw():
    """
    Fixture to load web scrape html from an html file for testing.
    """
    fname = os.path.join(
        os.path.dirname(__file__), "tests/fixture_csvs/stats_html.html"
    )


@pytest.fixture(scope="session")
def player_transformed_stats_data():
    """
    Fixture to load player stats data from a csv file for testing.
    """
    fname = os.path.join(
        os.path.dirname(__file__), "tests/fixture_csvs/player_stats_data.csv"
    )
    stats = pd.read_csv(fname)
    stats_transformed = get_player_stats_transform(stats)
    return stats_transformed
