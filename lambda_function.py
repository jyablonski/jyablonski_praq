from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timezone, timedelta
import boto3
import logging
from sqlalchemy import exc, create_engine
import os

# starting logging
logging.basicConfig(filename='example.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('Starting Logging Function')

# getting datetime vars
today = datetime.now().date()
yesterday = today - timedelta(1)
day = (datetime.now() - timedelta(1)).day
month = (datetime.now() - timedelta(1)).month
year = (datetime.now() - timedelta(1)).year

# defining scraping functions
def get_player_stats():
    year = 2021
    url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
    html = urlopen(url)
    soup = BeautifulSoup(html)

    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
    headers = headers[1:]

    rows = soup.findAll('tr')[1:]
    player_stats = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]

    stats = pd.DataFrame(player_stats, columns = headers)
    stats['PTS'] = pd.to_numeric(stats['PTS'])
    logging.info(f'General Stats Function Successful, retrieving {len(stats)} updated rows')
    return(stats)

def get_boxscores(month = month, day = day, year = year):
    url = "https://www.basketball-reference.com/friv/dailyleaders.fcgi?month={}&day={}&year={}&type=all".format(month, day, year)
    html = urlopen(url)
    soup = BeautifulSoup(html)

    try: 
        headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
        headers = headers[1:]
        headers[2] = "Location"
        headers[4] = "Outcome"

        rows = soup.findAll('tr')[1:]
        player_stats = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]

        df = pd.DataFrame(player_stats, columns = headers)
        df[['FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc']] = df[['FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc']].apply(pd.to_numeric)

        df.sort_values('PTS', ascending = False)
        logging.info(f'Box Score Function Successful, retrieving {len(df)} rows for {yesterday}')
        return(df)
    except IndexError:
        logging.info(f"Box Score Function Failed, no data available for {yesterday}")
        return pd.DataFrame()

def get_injuries():
    url = "https://www.basketball-reference.com/friv/injuries.fcgi"
    df = pd.read_html(url)[0]
    df = df.rename(columns = {"Update": "Date"})
    df['Scrape_Date'] = datetime.now()
    logging.info(f'Injury Function Successful, retrieving {len(df)} rows')
    return(df)

def get_transactions():
    url = "https://www.basketball-reference.com/leagues/NBA_2021_transactions.html"
    html = urlopen(url)
    soup = BeautifulSoup(html)
    trs = soup.findAll('li')[71:] # theres a bunch of garbage in the first 71 rows - no matter what 
    rows = []
    mylist = []
    for tr in trs:
        date = tr.find('span')
        if date is not None: # needed bc span can be null (multi <p> elements per span)
            date = date.text
        data = tr.findAll('p')
        for p in data:
            mylist.append(p.text)
        data3 = [date] + [mylist]
        rows.append(data3)
        mylist = []

    transactions = pd.DataFrame(rows)
    transactions.columns = ['Date', 'Transaction']
    transactions = transactions.explode('Transaction')
    transactions['Date'] = pd.to_datetime(transactions['Date'])
    transactions = transactions.query('Date != "NaN"')
    transactions
    logging.info(f'Transactions Function Successful, retrieving {len(transactions)} rows')
    return(transactions)

schedule_df = pd.DataFrame()
def schedule_scraper(month):
    global schedule_df
    url = "https://www.basketball-reference.com/leagues/NBA_2021_games-{}.html".format(month)
    html = urlopen(url)
    soup = BeautifulSoup(html)

    headers = [th.getText() for th in soup.findAll('tr')[0].findAll('th')]

    headers[6] = 'boxScoreLink'
    headers[7] = 'isOT'
    headers = headers[1:]

    rows = soup.findAll('tr')[1:]
    date_info = [[th.getText() for th in rows[i].findAll('th')]
            for i in range(len(rows))]

    game_info = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]
    date_info = [i[0] for i in date_info]

    schedule = pd.DataFrame(game_info, columns = headers)
    schedule['Date'] = date_info
    
    schedule_df = schedule_df.append(schedule)
    logging.info(f'Schedule Function Completed, retrieving {len(schedule_df)} rows')

def get_advanced_stats():
    url = "https://www.basketball-reference.com/leagues/NBA_2021.html"
    df = pd.read_html(url)
    df = pd.DataFrame(df[10])
    df.drop(columns = df.columns[0], 
        axis=1, 
        inplace=True)

    df.columns = ['Team', 'Age', 'W', 'L', 'PW', 'PL', 'MOV', 'SOS', 'SRS', 'ORTG', 'DRTG', 'NRTG', 'Pace', 'FTr', '3PAr', 'TS%', 'bby1', 'eFG%', 'TOV%', 'ORB%', 'FT/FGA', 'bby2', 'eFG%_opp', 'TOV%_opp', 'DRB%_opp', 'FT/FGA_opp', 'bby3', 'Arena', 'Attendance', 'Att/Game']
    df.drop(['bby1', 'bby2', 'bby3'], axis = 1, inplace = True)
    df = df.query('Team != "League Average"')
    logging.info(f'Advanced Stats Function Successful, retrieving updated data for 30 rows')
    return(df)

def get_odds():
    url = "https://sportsbook.draftkings.com/leagues/basketball/88673861?category=game-lines&subcategory=game"
    df = pd.read_html(url)
    data1 = df[0]
    data2 = df[1]
    data2 = data2.rename(columns = {"Tomorrow": "Today"})
    data = data1.append(data2)
    data
    data['SPREAD'] = data['SPREAD'].str[:-4]
    data['TOTAL'] = data['TOTAL'].str[:-4]
    data['TOTAL'] = data['TOTAL'].str[2:]
    data.reset_index(drop = True)
    data

    data['Today'] = data['Today'].str.replace("AM|PM", " ")
    data['Today'] = data['Today'].str.split().str[1:2]
    data['Today'] = pd.DataFrame([str(line).strip('[').strip(']').replace("'","") for line in data['Today']])
    data = data.rename(columns = {"Today": "team", "SPREAD": "spread", "TOTAL": "total_pts", "MONEYLINE": "moneyline"})
    data['Scrape_Date'] = datetime.now()
    logging.info(f'Odds Function Successful, retrieving {len(data)} rows')
    return(data)


# Scraping Functions
player_stats = get_player_stats()
box_scores = get_boxscores()
injury_data = get_injuries()
transactions = get_transactions()

month_list = ['december', 'january', 'february', 'march', 'april', 'may', 'june', 'july']
schedule_df = pd.DataFrame()
for month in month_list:
    schedule_scraper(month)

advanced_stats = get_advanced_stats()
odds = get_odds()
logs = pd.read_csv('example.log', sep=r'\\t', engine='python', header = None)

### Writing Dataframes to SQL
def sql_connection():
    try:
        connection = create_engine('mysql+mysqlconnector://' + os.environ.get('RDS_USER') + ':' + os.environ.get('RDS_PW') + '@' + os.environ.get('IP') + ':' + os.environ.get('PORT') + '/' + os.environ.get('RDS_DB'),
                     echo = False)
        logging.info('SQL Connection Successful')
        return(connection)
    except exc.SQLAlchemyError as e:
        logging.error('SQL Connection Failed, Error:', e)
        return e

player_stats.to_sql(con = connection, name = "player_stats", index = False, if_exists = "replace")
box_scores.to_sql(con = connection, name = "box_scores", index = False, if_exists = "append")
injury_data.to_sql(con = connection, name = "injury_data", index = False, if_exists = "append")
transactions.to_sql(con = connection, name = "transactions", index = False, if_exists = "replace")
schedule_df.to_sql(con = connection, name = "schedule", index = False, if_exists = "replace")
advanced_stats.to_sql(con = connection, name = "advanced_stats", index = False, if_exists = "replace")
odds.to_sql(con = connection, name = "odds", index = False, if_exists = "append")
logs.to_sql(con = connection, name = "lambda_logs", index = False, if_exists = "append")