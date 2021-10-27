import psycopg2
import os

db_settings = {
    'database'        : 'app',
    'user'            : 'app',
    'host'            : 'app',
    'port'            : 'app',
    'password'        : 'app',
    'application_name': 'app',
}

# DB setting for non-test env
if not os.environ.get('TEST'):
    dbc = psycopg2.connect(**db_settings)
    dbc.autocommit = True
else:
	# if we are in test return dummy object we will override by mock
	dbc = None
