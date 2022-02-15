import os
import pytest
import boto3
from botocore.exceptions import ClientError
from moto import mock_s3, mock_ses
import pandas as pd
from ... utils import *
class MyModel(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def save(self):
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.put_object(Bucket='mybucket', Key=self.name, Body=self.value)

@mock_ses
def test_ses_email(aws_credentials):
    ses = boto3.client("ses", region_name="us-east-1")
    logs = pd.DataFrame({'errors': ['ex1', 'ex2', 'ex3']})
    send_aws_email(logs)
    assert ses.verify_email_identity(EmailAddress="jyablonski9@gmail.com")
# import pandas as pd

@mock_ses
def test_ses_email2(aws_credentials):
    ses = boto3.client("ses", region_name="us-east-1")
    logs = pd.DataFrame({'errors': ['ex1', 'ex2', 'ex3']})
    send_aws_email(logs)
    send_quota = ses.get_send_quota()
    sent_count = int(send_quota["SentLast24Hours"])
    assert sent_count == 0


def test_player_stats_sql(setup_database, player_stats_data):
    # Test to make sure that there are 2 items in the database
    df = player_stats_data
    print(len(df))
    cursor = setup_database.cursor()
    df.to_sql(con=setup_database, name="player_stats", index=False, if_exists="replace")
    df_len = len(list(cursor.execute("SELECT * FROM player_stats")))
    cursor.close()
    assert df_len >= 300


def test_boxscores_sql(setup_database, boxscores_data):
    # Test to make sure that there are 2 items in the database
    df = boxscores_data
    print(len(df))
    cursor = setup_database.cursor()
    df.to_sql(con=setup_database, name="boxscores", index=False, if_exists="replace")
    df_len = len(list(cursor.execute("SELECT * FROM boxscores")))
    cursor.close()
    assert df_len >= 20


def test_opp_stats_sql(setup_database, opp_stats_data):
    # Test to make sure that there are 2 items in the database
    df = opp_stats_data
    print(len(df))
    cursor = setup_database.cursor()
    df.to_sql(con=setup_database, name="opp_stats", index=False, if_exists="replace")
    df_len = len(list(cursor.execute("SELECT * FROM opp_stats")))
    cursor.close()
    assert df_len == 30


def test_injuries_sql(setup_database, injuries_data):
    # Test to make sure that there are 2 items in the database
    df = injuries_data
    print(len(df))
    cursor = setup_database.cursor()
    df.to_sql(con=setup_database, name="injuries", index=False, if_exists="replace")
    df_len = len(list(cursor.execute("SELECT * FROM injuries")))
    cursor.close()
    assert df_len >= 10


def test_transactions_sql(setup_database, transactions_data):
    # Test to make sure that there are 2 items in the database
    df = transactions_data
    print(len(df))
    cursor = setup_database.cursor()
    df.to_sql(con=setup_database, name="transactions", index=False, if_exists="replace")
    df_len = len(list(cursor.execute("SELECT * FROM transactions")))
    cursor.close()
    assert df_len >= 50


def test_advanced_stats_sql(setup_database, advanced_stats_data):
    # Test to make sure that there are 2 items in the database
    df = advanced_stats_data
    print(len(df))
    cursor = setup_database.cursor()
    df.to_sql(
        con=setup_database, name="advanced_stats", index=False, if_exists="replace"
    )
    df_len = len(list(cursor.execute("SELECT * FROM advanced_stats")))
    cursor.close()
    assert df_len == 31


# def test_contracts_cols(contracts_data):
#     assert len(contracts_data.columns) == 4


def test_player_stats_rows(player_stats_data):
    assert len(player_stats_data) >= 300


def test_player_stats_cols(player_stats_data):
    assert len(player_stats_data.columns) == 30

def test_player_transformed_stats_rows(player_transformed_stats_data):
    assert len(player_transformed_stats_data) >= 300


def test_player_transformed_stats_cols(player_transformed_stats_data):
    assert len(player_transformed_stats_data.columns) == 30


def test_boxscores_cols(boxscores_data):
    assert len(boxscores_data.columns) == 29


def test_boxscores_rows(boxscores_data):
    assert len(boxscores_data) >= 20


def test_opp_stats_cols(opp_stats_data):
    assert len(opp_stats_data.columns) == 6


def test_opp_stats_rows(opp_stats_data):
    assert len(opp_stats_data) == 30


def test_injuries_cols(injuries_data):
    assert len(injuries_data.columns) == 5


def test_injuries_rows(injuries_data):
    assert len(injuries_data) >= 10


def test_transactions_cols(transactions_data):
    assert len(transactions_data.columns) == 3


def test_transactions_rows(transactions_data):
    assert len(transactions_data) >= 50


def test_advanced_stats_cols(advanced_stats_data):
    assert len(advanced_stats_data.columns) == 29  ##


def test_advanced_stats_rows(advanced_stats_data):
    assert len(advanced_stats_data) == 31

# def test_s3(s3_data):
#     assert s3_data == 'is awesome'

@mock_s3
def test_my_model_save():
    conn = boto3.resource('s3', region_name='us-east-1')
    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    conn.create_bucket(Bucket='mybucket')
    model_instance = MyModel('jacob', 'is awesome')
    model_instance.save()
    body = conn.Object('mybucket', 'jacob').get()['Body'].read().decode("utf-8")
    assert body == 'is awesome'

def test_my_model_save2():
    with mock_s3():
        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket='mybucket')

        model_instance = MyModel('steve', 'is awesome')
        model_instance.save()

        body = conn.Object('mybucket', 'steve').get()[
            'Body'].read().decode("utf-8")

        assert body == 'is awesome'

# def test_jacobs_s3(s3_data):
#     assert s3_data == 'is awesome'

def test_create_bucket(s3):
    # s3 is a fixture defined above that yields a boto3 s3 client.
    # Feel free to instantiate another boto3 S3 client -- Keep note of the region though.
    s3.create_bucket(Bucket="somebucket")
    result = s3.list_buckets()
    assert len(result['Buckets']) == 1
    assert result['Buckets'][0]['Name'] == 'somebucket'

# def test_odds_cols(odds_data):
#     assert len(odds_data.columns) >= 6

# def test_odds_rows(odds_data):
#     assert len(odds_data) >= 1


# def test_pbp_cols(pbp_data):
#     assert len(pbp_data.columns) == 13

# def test_pbp_rows(pbp_data):
#     assert len(pbp_data) >= 100

def test_col_dtypes(dummy_data):
    cols = dummy_data.dtypes.to_dict()

    fixture_cols = {
                    'col1': np.dtype('int64'),
                    'col2': np.dtype('int64'),
    }

    assert fixture_cols == cols