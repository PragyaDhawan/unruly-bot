"""
app/services/session.py
Manages per-user conversation state in memory.
In production, swap the dict for Redis for persistence across restarts.
"""

from datetime import datetime

# In-memory store: { chat_id: session_dict }
_sessions: dict = {}

# ── All possible states in the conversation flow ──────────────────────────────
STATES = {
    "START":              "Initial greeting",
    "GET_NAME":           "Waiting for full name",
    "GET_EMAIL":          "Waiting for email",
    "GET_PHONE":          "Waiting for phone number",
    "GET_INSTAGRAM":      "Waiting for Instagram handle",
    "GET_OTHER_SOCIALS":  "Waiting for TikTok/Snap/YouTube/X links",
    "REVIEWING":          "Pulling social metrics (async)",
    "DISQUALIFIED":       "Creator did not meet threshold",
    "GET_MONETIZATION":   "Waiting for monetization selection",
    "GET_GOALS":          "Waiting for goals selection",
    "ROUTING":            "Routing to TA team member",
    "DONE":               "Flow complete",
}


def get_session(chat_id: int) -> dict:
    """Returns existing session or creates a fresh one."""
    if chat_id not in _sessions:
        _sessions[chat_id] = _new_session()
    return _sessions[chat_id]


def update_session(chat_id: int, updates: dict):
    """Merges updates into an existing session."""
    session = get_session(chat_id)
    session.update(updates)
    _sessions[chat_id] = session


def clear_session(chat_id: int):
    """Resets session — used when user sends /start again."""
    _sessions[chat_id] = _new_session()


def set_state(chat_id: int, state: str):
    update_session(chat_id, {"state": state})


def get_state(chat_id: int) -> str:
    return get_session(chat_id).get("state", "START")


def save_field(chat_id: int, field: str, value):
    """Saves a single collected data field into the session."""
    session = get_session(chat_id)
    session["data"][field] = value
    _sessions[chat_id] = session


def get_data(chat_id: int) -> dict:
    return get_session(chat_id).get("data", {})


def _new_session() -> dict:
    return {
        "state": "START",
        "data": {
            "name":              None,
            "email":             None,
            "phone":             None,
            "instagram":         None,
            "other_socials":     None,
            "followers":         None,
            "avg_likes":         None,
            "avg_comments":      None,
            "engagement_rate":   None,
            "monetization":      [],   # multi-select
            "goals":             [],   # multi-select
            "qualified":         None,
            "assigned_ta":       None,
            "date_submitted":    None,
            "call_status":       "Pending",
        },
        "pending_selections": {
            "monetization": [],
            "goals": [],
        },
        "created_at": datetime.utcnow().isoformat(),
    }
