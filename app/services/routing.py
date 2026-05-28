"""
app/services/routing.py
Assigns a TA team member and generates the introduction message.
TA members are loaded from .env as a comma-separated list.
"""

import itertools
from config.settings import TA_MEMBERS

# Round-robin counter so each TA gets equal leads
_counter = itertools.cycle(range(max(len(TA_MEMBERS), 1)))


def assign_ta() -> str:
    """
    Returns the next TA member's Telegram handle using round-robin.
    Falls back to a placeholder if TA_MEMBERS is not configured.
    """
    if not TA_MEMBERS:
        return "@unruly_team"
    index = next(_counter) % len(TA_MEMBERS)
    return TA_MEMBERS[index]


def build_intro_message(creator_data: dict, ta_handle: str) -> str:
    """
    Builds the handoff intro message sent to the creator.
    Matches the exact template from the assessment doc.
    """
    name          = creator_data.get("name", "there")
    instagram     = creator_data.get("instagram", "")
    other_socials = creator_data.get("other_socials", "")
    followers     = creator_data.get("followers", 0)
    engagement    = creator_data.get("engagement_rate", 0)

    # Build social links line
    social_link = f"https://instagram.com/{instagram}" if instagram else other_socials

    # TA first name only for friendlier message
    ta_name = ta_handle.lstrip("@").replace("_", " ").title()

    return (
        f"Hi <b>{name}</b>! 🎉 Thanks so much for submitting.\n\n"
        f"I'm introducing you to <b>{ta_name}</b> from Unruly — "
        f"they'll help set up a quick call with you!\n\n"
        f"📸 <b>Social:</b> {social_link}\n"
        f"👥 <b>Followers:</b> {followers:,}\n"
        f"📊 <b>Engagement Rate:</b> {engagement}%\n\n"
        f"<b>{ta_name}</b> will be in touch shortly. "
        f"We're excited to connect! 🚀"
    )


def build_ta_alert(creator_data: dict, ta_handle: str) -> str:
    """
    Internal alert message for the TA team member.
    Sent separately to notify them of a new qualified lead.
    """
    name         = creator_data.get("name", "Unknown")
    email        = creator_data.get("email", "N/A")
    phone        = creator_data.get("phone", "N/A")
    instagram    = creator_data.get("instagram", "N/A")
    followers    = creator_data.get("followers", 0)
    avg_likes    = creator_data.get("avg_likes", 0)
    engagement   = creator_data.get("engagement_rate", 0)
    assigned_ta = creator_data.get("assigned_ta", "Unassigned")
    monetization = ", ".join(creator_data.get("monetization", [])) or "N/A"
    goals        = ", ".join(creator_data.get("goals", [])) or "N/A"

    return (
        f"🔥 <b>New Qualified Creator!</b>\n\n"
        f"👤 <b>Assigned TA:</b> {assigned_ta}\n\n"
        f"👤 <b>Name:</b> {name}\n"
        f"📧 <b>Email:</b> {email}\n"
        f"📱 <b>Phone:</b> {phone}\n"
        f"📸 <b>Instagram:</b> @{instagram}\n"
        f"👥 <b>Followers:</b> {followers:,}\n"
        f"❤️ <b>Avg Likes:</b> {avg_likes:,}\n"
        f"📊 <b>Engagement:</b> {engagement}%\n\n"
        f"💰 <b>Monetizes via:</b> {monetization}\n"
        f"🎯 <b>Looking for:</b> {goals}\n\n"
        f"<i>Please reach out and schedule a call!</i>"
    )
