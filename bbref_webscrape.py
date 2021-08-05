# %%
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timezone, timedelta
import boto3
import pyarrow
import awswrangler as wr
import logging

# %%
df = pd.DataFrame([1, 2])
logging.basicConfig(filename='example.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('Starting x Function')
if df.empty is True:
    logging.info('oh no df is empty')
else:
    logging.info(f'Printing {df.shape[0]} number of rows with shape')
    logging.info(f'Printing {len(df)} number of rows from df')
    logging.info(f'Printing {len(df.index)} number of rows from the dfindex????')
    logging.info(f'Printing {df.empty} number of rows')

logging.info('Finishing x Function')
logging.info('temp logging file should get written to google drive here')
logging.shutdown()

# %%
# NBA season we will be analyzing
year = 2021
# URL page we will scraping (see image above)
url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
# this is the HTML from the given URL
html = urlopen(url)
soup = BeautifulSoup(html)

# %%
url
# url is literlly just the url link

# %%
html
# this is the httpresponse code we get after opening the url

# %%
# soup
# soup is the LITERAL HTML.  ITS HUNDREDS OF LINES LONG, THOUSANDS

# we need to grab just the elements we want.

# %%
# use findALL() to get the column headers
# soup.findAll('tr', limit=2)
# use getText()to extract the text we need into a list

# the tr group has th elements which are the headers we want data for.
headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]

# exclude the first column as we will not need the ranking order from Basketball Reference for the analysis
headers = headers[1:]
headers

# %%
# avoid the first header row
# the td elements have the actual data points we want.
rows = soup.findAll('tr')[1:]
player_stats = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]

# %%
# combining the column headers and the data points together
stats = pd.DataFrame(player_stats, columns = headers)
stats['PTS'] = pd.to_numeric(stats['PTS'])

# %%
stats.sort_values('PTS', ascending = False).head(10)

# %%
# datetimte stuff
today = datetime.now().date()
yesterday = today - timedelta(1)
day = (datetime.now() - timedelta(1)).day
month = (datetime.now() - timedelta(1)).month
year = (datetime.now() - timedelta(1)).year

# %%
#### BOX SCORE WEB SCRAPING
# https://www.basketball-reference.com/friv/dailyleaders.fcgi?month=07&day=17&year=2021&type=all

url = "https://www.basketball-reference.com/friv/dailyleaders.fcgi?month={}&day={}&year={}&type=all".format(month, day, year)
html = urlopen(url)
soup = BeautifulSoup(html)

# %%
headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
headers = headers[1:]
headers[2] = "Location"
headers[4] = "Outcome"
# headers

# %%
rows = soup.findAll('tr')[1:]
player_stats = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]

# %%
df2 = pd.DataFrame(player_stats, columns = headers)

# %%
df2[['FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc']] = df2[['FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc']].apply(pd.to_numeric)

# %%
df2.sort_values('PTS', ascending = False)

# %%
#### injury report
url = "https://www.basketball-reference.com/friv/injuries.fcgi"
html = urlopen(url)
soup = BeautifulSoup(html)

# %%
headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]

trs = soup.findAll('tr')[1:]
rows = []
for tr in trs:
    player_name = tr.find('a').text
    data = [player_name] + [x.text for x in tr.find_all('td')]
    rows.append(data)

injury_data = pd.DataFrame(rows, columns = headers)

# %%
injury_data

# %%
# ALTERNATIVE
injury_data2 = pd.read_html(url)[0]

# %%
injury_data2

# %%
##### transactions
url = "https://www.basketball-reference.com/leagues/NBA_2021_transactions.html"
html = urlopen(url)
soup = BeautifulSoup(html)

# %%
headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]

trs = soup.findAll('tr')[1:]
rows = []
for tr in trs:
    player_name = tr.find('a').text
    data = [player_name] + [x.text for x in tr.find_all('td')]
    rows.append(data)

injury_data = pd.DataFrame(rows, columns = headers)

# %%
#for tr in trs:
    #data = tr.findAll('p')
    # for p in data:
        # print(p.text)
    # print(tr.find('span').text)
    # print(x.text for x in tr.find('p'))

# %%
trs = soup.findAll('li')[71:]
rows = []
for tr in trs:
    date = tr.find('span').text
    data = tr.find('p')
    data2 = [date] + [data]
    rows.append(data2)

# %%


# %%
trs = soup.findAll('li')[71:]
rows = []
mylist = []
for tr in trs:
    date = tr.find('span').text
    data = tr.findAll('p')
    for p in data:
        if p is not None:
            mylist.append(p.text)
    data3 = [date] + [mylist]
    rows.append(data3)
    mylist = []

# %%
trs = soup.findAll('li')[71:]
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

# %%
transactions = pd.DataFrame(rows)
transactions.columns = ['Date', 'Transaction']
transactions = transactions.explode('Transaction')
transactions['Date'] = pd.to_datetime(transactions['Date'])
transactions = transactions.query('Date != "NaN"')
transactions

# %%
# random web scrape i found - might be useful
import csv 
import requests
from bs4 import BeautifulSoup
import csv
import re
url_list = ['https://basketball.realgm.com/player/player/Summary/2',
            'https://basketball.realgm.com/player/player/Summary/1']

for url in url_list:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    player = soup.find_all('div', class_='wrapper clearfix container')[0]

    playerprofile = re.sub(
        r'\n\s*\n', r'\n', player.get_text().strip(), flags=re.M)

    output = playerprofile + "\n"


# %%
### SCHEDULE
raw_df = pd.DataFrame()
month_list = ['december', 'january', 'february', 'march', 'april', 'may', 'june', 'july']
url = "https://www.basketball-reference.com/leagues/NBA_2021_games-december.html"
html = urlopen(url)
soup = BeautifulSoup(html)

# %%
headers = [th.getText() for th in soup.findAll('tr')[0].findAll('th')]
# headers = headers[1:]
headers[6] = 'boxScoreLink'
headers[7] = 'isOT'
headers = headers[1:]

# %%
rows = soup.findAll('tr')[1:]
player_stats = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]

# %%
rows = soup.findAll('tr')[1:]
date_info = [[th.getText() for th in rows[i].findAll('th')]
            for i in range(len(rows))]

game_info = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]
date_info = [i[0] for i in date_info] # removes brackets from each element.
# date_info

# %%
schedule = pd.DataFrame(game_info, columns = headers)
schedule['Date'] = date_info

# %%
# variables in functions are local by default
# variables outside of functions are global by default
# to modify a global variable in local function, we have to explicity label it as a global var.
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
    
    # join_df = join_df.append(schedule)
    schedule_df = schedule_df.append(schedule)
    # return(join_df)

# %%
schedule_df = pd.DataFrame()
schedule_scraper('february')

# %%
schedule_df = pd.DataFrame()
for month in month_list:
    schedule_scraper(month)

# %%
raw_df.tail(5)

# %%
print(f"hi it is {month} haa")
aab = f'hi it is {month} haa'
print(aab)
# f('hii {var1} haa' functionality works for both print statements and variable dec

# %%
print('hi it is {} month') #.format(month) will give an error
aac = 'hi it is {} haa'.format(month)
print(aab)
# {} .format only works for variable dec

# %%
#### Team advanced stats
url = "https://www.basketball-reference.com/leagues/NBA_2021.html"
html = urlopen(url)
soup = BeautifulSoup(html)

# %%
# NOT NEEDED
divTag = soup.find("div", {"id": "div_advanced-team"})
th_all = divTag.find_all('th')
result = []
for th in th_all:
    result.extend(th.find_all(text='A'))

bby = divTag.select("th td")

# %%
df_list = pd.read_html(url)


# %%
advanced_stats = pd.DataFrame(df_list[10])
advanced_stats.drop(columns=advanced_stats.columns[0], 
        axis=1, 
        inplace=True)

advanced_stats.columns = ['Team', 'Age', 'W', 'L', 'PW', 'PL', 'MOV', 'SOS', 'SRS', 'ORTG', 'DRTG', 'NRTG', 'Pace', 'FTr', '3PAr', 'TS%', 'bby1', 'eFG%', 'TOV%', 'ORB%', 'FT/FGA', 'bby2', 'eFG%_opp', 'TOV%_opp', 'DRB%_opp', 'FT/FGA_opp', 'bby3', 'Arena', 'Attendance', 'Att/Game']
advanced_stats.drop(['bby1', 'bby2', 'bby3'], axis = 1, inplace = True)
# advanced_stats.head(5)

# %%
# SQL STUFF
import sqlalchemy
from mysql.connector import Error
import os

def create_connection():
        connection = None
        try:
            connection = sqlalchemy.create_engine('mysql+mysqlconnector://' + os.environ.get('USER') + ':' + os.environ.get('PW') + '@' + os.environ.get('IP') + ':' + os.environ.get('PORT') + '/' + os.environ.get('DB'),
                        echo = False)
            print(f"Connection to Jacob's RDS MySQL {os.environ.get('DB')} DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection

# connection = create_connection("localhost", "root", "")

# %%
connection = create_connection()

# %%
# unnecessary for sqlalchemy, only used for mysql.connector + cursor connections
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

# %%
all_tables = pd.read_sql_query('SHOW TABLES FROM aws_database;', connection)
all_tables

# %%
odds = pd.read_sql_query('SELECT * FROM aws_new_odds;', connection)
odds

# %%
odds.to_sql(con = connection, name = "my_python_table_2", index = False, if_exists = "replace")

# %%
odds2 = pd.read_sql_query('SELECT * FROM my_python_table_2;', con = connection)

# %%
time_now = pd.Series(datetime.now())
time_df = pd.DataFrame()
time_df = time_df.append(time_now, ignore_index = True)
time_df.to_sql(con = connection, name = "my_python_time_table", index = False, if_exists = "append")

# %%
time_df.to_sql(con = connection, name = "my_python_time_table", index = False, if_exists = "replace")

# %%
odds_sql = pd.read_sql_query('SELECT * FROM my_python_time_table;', connection)
odds_sql

# %%
# append rows of your local dataframe to an EXISTING sql table
time_df.to_sql(con = connection, name = "my_python_time_table",
               index = False, if_exists = "append")

# overwrite your EXISTING sql table with the new dataframe.
time_df.to_sql(con = connection, name = "my_python_time_table",
               index = False, if_exists = "replace")

# %%
# S3 STUFF
s3 = boto3.resource(
    service_name ='s3',
    region_name = os.getenv('AWS_REGION'),
    aws_access_key_id = os.getenv('AWS_KEY'),
    aws_secret_access_key = os.getenv('AWS_SECRET')
)

# %%
for bucket in s3.buckets.all():
    print(bucket.name)

# %%
advanced_stats.to_parquet('advanced_stats.parquet')

# uploading a file to the bucket mygamelogsbucket
s3.Bucket('mygamelogsbucket').upload_file(Filename = 'foo.parquet', Key = 'you_dont_need_extension')

# %%
# works but spits out error.
wr.s3.to_parquet(
    df = advanced_stats,
    path = "s3://mygamelogsbucket/my-advanced-stats4.parquet"
    #path2 = "s3://mygamelogsbucket/key/my-advanced-stats3" will make a folder called key
    # and put the my-advanced-stats3 file in the key folder.
)

# %%
gamelogs_s3 = s3.Bucket('mygamelogsbucket').Object('bby.csv').get()
gamelogs_s3 = pd.read_csv(gamelogs_s3['Body'], index_col = 0)


# %%
gamelogs_s3.tail(5)

# %%
# works but spits out error.
wr.s3.to_parquet(
    df = gamelogs_s3,
    path = "s3://mygamelogsbucket/bby.parquet"
    #path2 = "s3://mygamelogsbucket/key/my-advanced-stats3" will make a folder called key
    # and put the my-advanced-stats3 file in the key folder.
)

# %%
s3_df_parquet = wr.s3.read_parquet("s3://mygamelogsbucket/bby.parquet")
# s3_df_parquet2 = pd.read_parquet("s3://mygamelogsbucket/bby.parquet")
# need different permissions to access this.