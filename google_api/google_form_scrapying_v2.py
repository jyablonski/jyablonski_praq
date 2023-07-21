import gspread
import pandas as pd

# https://docs.gspread.org/en/latest/oauth2.html
# create new project from google developer console
# create new service account from `APIs & Services -> Credentials -> Service Account`
# create a new key for the service account
# share the google sheet with the `client_email` provided in the service account json creds
# enable google sheets api in the project

url = "https://docs.google.com/spreadsheets/d/zzz"

# creds = {
#   "type": "service_account",
#   "project_id": "z",
#   "private_key_id": "4",
#   "private_key": "-a",
#   "client_email": "d",
#   "client_id": "1b",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "c",
#   "universe_domain": "googleapis.com"
# }
# gc = gspread.service_account_from_dict(creds)


gc = gspread.service_account(
    filename="g_service_creds.json"
)  # do this 1 time and get a saved token forever.
sh = gc.open_by_url(url)

worksheet = sh.get_worksheet(0)

df = pd.DataFrame(worksheet.get_all_records())
