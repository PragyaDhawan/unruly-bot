# test_sheets.py
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config.settings import (
    GOOGLE_SHEET_ID,
    GOOGLE_SERVICE_ACCOUNT_JSON,
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

print("Using Sheet ID:", GOOGLE_SHEET_ID)
print("Using credentials file:", GOOGLE_SERVICE_ACCOUNT_JSON)

creds = Credentials.from_service_account_file(
    GOOGLE_SERVICE_ACCOUNT_JSON,
    scopes=SCOPES,
)

service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()

row = [["TEST", "HELLO", "FROM BOT"]]

result = sheet.values().append(
    spreadsheetId=GOOGLE_SHEET_ID,
    range="Sheet1!A:C",
    valueInputOption="USER_ENTERED",
    insertDataOption="INSERT_ROWS",
    body={"values": row},
).execute()

print("SUCCESS")
print(result)