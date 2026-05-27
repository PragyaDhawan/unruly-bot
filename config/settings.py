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

# ── OPENAI ─────────────────────────────────────────────────────────────────
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL       = "gpt-4o"   # Best balance of speed + quality

# ── SOCIAL METRICS ────────────────────────────────────────────────────────────
PHYLLO_CLIENT_ID     = os.getenv("PHYLLO_CLIENT_ID")
PHYLLO_CLIENT_SECRET = os.getenv("PHYLLO_CLIENT_SECRET")
HYPEAUDITOR_API_KEY  = os.getenv("HYPEAUDITOR_API_KEY")

# ── VALIDATION ────────────────────────────────────────────────────────────────
ABSTRACT_API_KEY = os.getenv("ABSTRACT_API_KEY")

# ── GOOGLE SHEETS ─────────────────────────────────────────────────────────────
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json")
GOOGLE_SHEET_ID             = os.getenv("GOOGLE_SHEET_ID")

# ── MONDAY CRM ────────────────────────────────────────────────────────────────
MONDAY_API_KEY  = os.getenv("MONDAY_API_KEY")
MONDAY_BOARD_ID = os.getenv("MONDAY_BOARD_ID")

# ── SLACK ─────────────────────────────────────────────────────────────────────
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# ── TALENT ACQUISITION TEAM ───────────────────────────────────────────────────
# Format in .env: @jordan_unruly,@priya_unruly
_ta_raw = os.getenv("TA_MEMBERS", "")
TA_MEMBERS = [m.strip() for m in _ta_raw.split(",") if m.strip()]

# ── QUALIFICATION THRESHOLDS ──────────────────────────────────────────────────
# Edit these to change who gets qualified — no code changes needed elsewhere
MIN_FOLLOWERS  = 10_000
MIN_AVG_LIKES  = 1_000

# ── APP ───────────────────────────────────────────────────────────────────────
APP_ENV = os.getenv("APP_ENV", "development")
PORT    = int(os.getenv("PORT", 8000))


def validate_config():
    """
    Call this at startup to catch missing env vars early.
    Prints a clear error for each missing key.
    """
    required = {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "ANTHROPIC_API_KEY":  ANTHROPIC_API_KEY,
        "ABSTRACT_API_KEY":   ABSTRACT_API_KEY,
        "GOOGLE_SHEET_ID":    GOOGLE_SHEET_ID,
        "MONDAY_API_KEY":     MONDAY_API_KEY,
        "MONDAY_BOARD_ID":    MONDAY_BOARD_ID,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print("⚠️  WARNING — Missing environment variables:")
        for key in missing:
            print(f"   ✗ {key}")
        print("   → Copy .env.example to .env and fill in the values.\n")
    else:
        print("✅ All required environment variables loaded.")
