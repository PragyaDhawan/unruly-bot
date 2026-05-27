"""
app/services/telegram.py
All functions for sending messages to Telegram.
Keeps webhook.py clean — only import from here to talk to Telegram.
"""

import requests
from config.settings import TELEGRAM_API_URL


def send_message(chat_id: int, text: str, parse_mode: str = "HTML") -> dict:
    """Send a plain text message."""
    payload = {
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": parse_mode,
    }
    r = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload, timeout=10)
    return r.json()


def send_inline_keyboard(chat_id: int, text: str, buttons: list, parse_mode: str = "HTML") -> dict:
    """
    Send a message with inline keyboard buttons.

    buttons format:
    [
        [{"text": "Label", "callback_data": "value"}],  # one per row
        [{"text": "A", "callback_data": "a"}, {"text": "B", "callback_data": "b"}],  # two per row
    ]
    """
    payload = {
        "chat_id":      chat_id,
        "text":         text,
        "parse_mode":   parse_mode,
        "reply_markup": {"inline_keyboard": buttons},
    }
    r = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload, timeout=10)
    return r.json()


def answer_callback_query(callback_query_id: str, text: str = "") -> dict:
    """Acknowledge a button tap (removes the loading spinner)."""
    payload = {"callback_query_id": callback_query_id, "text": text}
    r = requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json=payload, timeout=10)
    return r.json()


def edit_message_reply_markup(chat_id: int, message_id: int, buttons: list) -> dict:
    """Update the inline keyboard on an existing message (e.g. to show selections)."""
    payload = {
        "chat_id":      chat_id,
        "message_id":   message_id,
        "reply_markup": {"inline_keyboard": buttons},
    }
    r = requests.post(f"{TELEGRAM_API_URL}/editMessageReplyMarkup", json=payload, timeout=10)
    return r.json()


def send_typing(chat_id: int):
    """Show 'typing...' indicator while processing."""
    requests.post(
        f"{TELEGRAM_API_URL}/sendChatAction",
        json={"chat_id": chat_id, "action": "typing"},
        timeout=5
    )


# ── Pre-built keyboard layouts ────────────────────────────────────────────────

def monetization_keyboard(selected: list = []) -> list:
    """
    Inline keyboard for monetization question.
    Adds ✅ to already-selected options.
    """
    options = [
        ("💰 Brand Deals",              "mon_brand"),
        ("🔥 OnlyFans",                 "mon_of"),
        ("📸 Fanfix",                   "mon_fanfix"),
        ("💎 Fanvue",                   "mon_fanvue"),
        ("👻 Snapchat",                 "mon_snap"),
        ("🎵 TikTok",                   "mon_tiktok"),
        ("✉️ Telegram",                 "mon_telegram"),
        ("🔒 Subscriptions",            "mon_subs"),
        ("❌ No monetization yet",      "mon_none"),
    ]
    buttons = []
    for label, value in options:
        tick = "✅ " if value in selected else ""
        buttons.append([{"text": f"{tick}{label}", "callback_data": value}])

    # Confirm button at bottom
    buttons.append([{"text": "➡️ Continue", "callback_data": "mon_done"}])
    return buttons


def goals_keyboard(selected: list = []) -> list:
    """
    Inline keyboard for goals question.
    Adds ✅ to already-selected options.
    """
    options = [
        ("📈 More monthly income",              "goal_income"),
        ("🔐 Paywall management",               "goal_paywall"),
        ("👻 Snapchat monetization",            "goal_snap"),
        ("✉️ Telegram monetization",            "goal_telegram"),
        ("🔥 OnlyFans/Fanvue/Fanfix Mgmt",     "goal_of"),
        ("🤝 Brand deal support",               "goal_brand"),
        ("🎯 Content strategy",                 "goal_content"),
        ("⭐ Full-service management",          "goal_fullservice"),
    ]
    buttons = []
    for label, value in options:
        tick = "✅ " if value in selected else ""
        buttons.append([{"text": f"{tick}{label}", "callback_data": value}])

    buttons.append([{"text": "➡️ Continue", "callback_data": "goal_done"}])
    return buttons


# ── Human-readable label lookups ──────────────────────────────────────────────

MONETIZATION_LABELS = {
    "mon_brand":    "Brand Deals",
    "mon_of":       "OnlyFans",
    "mon_fanfix":   "Fanfix",
    "mon_fanvue":   "Fanvue",
    "mon_snap":     "Snapchat",
    "mon_tiktok":   "TikTok",
    "mon_telegram": "Telegram",
    "mon_subs":     "Subscriptions",
    "mon_none":     "No monetization yet",
}

GOALS_LABELS = {
    "goal_income":      "More monthly income",
    "goal_paywall":     "Paywall management",
    "goal_snap":        "Snapchat monetization",
    "goal_telegram":    "Telegram monetization",
    "goal_of":          "OnlyFans/Fanvue/Fanfix Management",
    "goal_brand":       "Brand deal support",
    "goal_content":     "Content strategy",
    "goal_fullservice": "Full-service management",
}
