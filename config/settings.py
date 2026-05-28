"""
config/settings.py
Loads and validates all environment variables on startup.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── TELEGRAM ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL   = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ── OPENAI ────────────────────────────────────────────────────────────────────
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL    = "gpt-4o-mini"   # Cheapest smart model — ~$0.15 per 1M tokens

# ── SOCIAL METRICS ────────────────────────────────────────────────────────────
RAPIDAPI_KEY         = os.getenv("RAPIDAPI_KEY")

# ── VALIDATION ────────────────────────────────────────────────────────────────
ABSTRACT_EMAIL_API_KEY = os.getenv("ABSTRACT_EMAIL_API_KEY")
ABSTRACT_PHONE_API_KEY = os.getenv("ABSTRACT_PHONE_API_KEY")
DEFAULT_PHONE_COUNTRY   = os.getenv("DEFAULT_PHONE_COUNTRY", "")  # optional, e.g. US

# ── GOOGLE SHEETS ─────────────────────────────────────────────────────────────
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json")
GOOGLE_SHEET_ID             = os.getenv("GOOGLE_SHEET_ID")

SKIP_EXTERNAL_VALIDATION = os.getenv("SKIP_EXTERNAL_VALIDATION", "false").lower() == "true"
SKIP_QUALIFICATION = os.getenv("SKIP_QUALIFICATION", "false").lower() == "true"

# ── TALENT ACQUISITION TEAM ───────────────────────────────────────────────────
_ta_raw = os.getenv("TA_MEMBERS", "")
TA_GROUP_CHAT_ID = os.getenv("TA_GROUP_CHAT_ID")
TA_MEMBERS = [m.strip() for m in _ta_raw.split(",") if m.strip()]

# ── QUALIFICATION THRESHOLDS ──────────────────────────────────────────────────
MIN_FOLLOWERS = 10_000
MIN_AVG_LIKES = 1_000

# ── APP ───────────────────────────────────────────────────────────────────────
APP_ENV = os.getenv("APP_ENV", "development")
PORT    = int(os.getenv("PORT", 8000))


def validate_config():
    """Call at startup to catch missing env vars early."""
    required = {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "OPENAI_API_KEY":     OPENAI_API_KEY,
        "ABSTRACT_EMAIL_API_KEY":   ABSTRACT_EMAIL_API_KEY,
        "ABSTRACT_PHONE_API_KEY":   ABSTRACT_PHONE_API_KEY,
        "GOOGLE_SHEET_ID":    GOOGLE_SHEET_ID,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print("⚠️  WARNING — Missing environment variables:")
        for key in missing:
            print(f"   ✗ {key}")
        print("   → Copy .env.example to .env and fill in the values.\n")
    else:
        print("✅ All required environment variables loaded.")
