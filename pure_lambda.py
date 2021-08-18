import logging
import os
from urllib.request import urlopen
# from bs4 import BeautifulSoup
from pandas import DataFrame, read_html, to_numeric
from sqlalchemy import exc, create_engine
import pymysql

print('LOADED FUNCTIONS')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_injuries():
    url = "https://www.basketball-reference.com/friv/injuries.fcgi"
    df = read_html(url)[0]
    logging.info(f'Injury Function Successful, retrieving {len(df)} rows')
    return(df)


def sql_connection():
    try:
        connection = create_engine('mysql+pymysql://' + os.environ.get('RDS_USER') + ':' + os.environ.get('RDS_PW') + '@' + os.environ.get('IP') + ':' + os.environ.get('PORT') + '/' + os.environ.get('RDS_DB'),
                     echo = False)
        logging.info('SQL Connection Successful')
        return(connection)
    except exc.SQLAlchemyError as e:
        logging.error('SQL Connection Failed, Error:', e)
        return e

print('STARTING HANDLER')
def lambda_handler(event, context):
    stats = get_injuries()
    conn3 = sql_connection()
    stats.to_sql(con=conn3, name="player_stats4", index=False, if_exists="replace")
