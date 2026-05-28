"""
app/services/storage.py

Handles:
- Google Sheets lead storage
- Monday CRM lead creation
- Slack/internal alerts
"""

import json
import requests

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config.settings import (
    GOOGLE_SHEET_ID,
    GOOGLE_SERVICE_ACCOUNT_JSON
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# ──────────────────────────────────────────────────────────────────────────────
# GOOGLE SHEETS
# ──────────────────────────────────────────────────────────────────────────────

def append_to_google_sheets(data: dict) -> bool:
    print("[storage] append_to_google_sheets CALLED")
    try:
        print("[storage] Initializing Google Sheets client...")

        creds = Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_JSON,
            scopes=SCOPES,
        )

        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        row = [
            data.get("name", ""),
            data.get("email", ""),
            "'" + str(data.get("phone", "")),
            data.get("instagram", ""),
            data.get("other_socials", ""),
            data.get("followers", 0),
            data.get("avg_likes", 0),
            data.get("avg_comments", 0),
            data.get("engagement_rate", 0),
            ", ".join(data.get("monetization", [])),
            ", ".join(data.get("goals", [])),
            "Yes" if data.get("qualified") else "No",
            data.get("assigned_ta", ""),
            data.get("date_submitted", ""),
            data.get("call_status", "Pending"),
        ]

        print("[storage] Row being appended:")
        print(row)

        result = sheet.values().append(
            spreadsheetId=GOOGLE_SHEET_ID,
            range="Sheet1!A:O",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]},
        ).execute()

        print("[storage] Google Sheets append SUCCESS")
        print(result)

        return True

    except Exception as e:
        print(f"[storage] Google Sheets ERROR: {e}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# MONDAY CRM
# ──────────────────────────────────────────────────────────────────────────────

# def create_monday_item(data: dict) -> bool:
#     """
#     Creates a new lead item in Monday CRM.
#     """

#     if not MONDAY_API_KEY or not MONDAY_BOARD_ID:
#         print("[storage] Monday config missing — skipping")
#         return False

#     query = """
#     mutation ($board_id: ID!, $item_name: String!, $column_values: JSON!) {
#       create_item(
#         board_id: $board_id,
#         item_name: $item_name,
#         column_values: $column_values
#       ) {
#         id
#       }
#     }
#     """

#     column_values = {
#         "email": {
#             "email": data.get("email", ""),
#             "text": data.get("email", ""),
#         },
#         "phone": data.get("phone", ""),
#         "status": {
#             "label": "New Lead"
#         },
#         "text": f"@{data.get('instagram', '')}",
#     }

#     payload = {
#         "query": query,
#         "variables": {
#             "board_id": int(MONDAY_BOARD_ID),
#             "item_name": data.get("name", "Unknown Lead"),
#             "column_values": json.dumps(column_values),
#         },
#     }

#     headers = {
#         "Authorization": MONDAY_API_KEY,
#         "Content-Type": "application/json",
#     }

#     try:
#         r = requests.post(
#             "https://api.monday.com/v2",
#             json=payload,
#             headers=headers,
#             timeout=15,
#         )

#         r.raise_for_status()

#         resp = r.json()

#         if "errors" in resp:
#             print("[storage] Monday errors:", resp["errors"])
#             return False

#         print("[storage] Monday item created")
#         return True

#     except Exception as e:
#         print(f"[storage] Monday error: {e}")
#         return False


# ──────────────────────────────────────────────────────────────────────────────
# SLACK ALERTS
# ──────────────────────────────────────────────────────────────────────────────

# def send_slack_alert(message: str) -> bool:
#     """
#     Sends internal Slack alert.
#     """

#     if not SLACK_WEBHOOK_URL:
#         print("[storage] Slack webhook missing — skipping")
#         return False

#     try:
#         r = requests.post(
#             SLACK_WEBHOOK_URL,
#             json={"text": message},
#             timeout=10,
#         )

#         if r.status_code == 200:
#             print("[storage] Slack alert sent")
#             return True

#         print("[storage] Slack failed:", r.text)
#         return False

#     except Exception as e:
#         print(f"[storage] Slack error: {e}")
#         return False


# ──────────────────────────────────────────────────────────────────────────────
# MASTER SAVE FUNCTION
# ──────────────────────────────────────────────────────────────────────────────

def save_submission(data: dict):
    """
    Centralized persistence for all creator submissions.
    Saves to:
      - Google Sheets
      - Monday CRM
    """
    print("[storage] save_submission CALLED")
    print("\n[storage] ===== SAVE SUBMISSION START =====")
    print(f"[storage] Creator: {data.get('name')}")
    print(f"[storage] Instagram: @{data.get('instagram')}")
    print(f"[storage] Qualified: {data.get('qualified')}")
    print(f"[storage] Call Status: {data.get('call_status')}")

    print("[storage] Sending to Google Sheets...")
    sheets_result = append_to_google_sheets(data)
    print(f"[storage] Google Sheets result: {sheets_result}")

    # print("[storage] Sending to Monday CRM...")
    # monday_result = create_monday_item(data)
    # print(f"[storage] Monday result: {monday_result}")

    print("[storage] ===== SAVE SUBMISSION END =====\n")