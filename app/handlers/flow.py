"""
app/handlers/flow.py
The brain of the bot. Handles every state transition.

Each handle_* function:
  - Receives (chat_id, text_or_data)
  - Reads/writes session
  - Sends the appropriate Telegram message
  - Advances the state
"""

from app.services import session as sess
from app.services.telegram import (
    send_message, send_inline_keyboard, send_typing,
    monetization_keyboard, goals_keyboard,
    MONETIZATION_LABELS, GOALS_LABELS,
)
from app.services.validation import validate_email, validate_phone, validate_instagram
from app.services.social_metrics import get_metrics, qualify_creator
from app.services.routing import assign_ta, build_intro_message, build_ta_alert
from config.settings import MIN_FOLLOWERS, MIN_AVG_LIKES


# ── Entry point — called on every incoming text message ──────────────────────

async def handle_message(chat_id: int, text: str):
    """Routes incoming text to the correct state handler."""

    # /start always resets
    if text.strip().lower() in ["/start", "/restart"]:
        sess.clear_session(chat_id)
        await handle_start(chat_id)
        return

    state = sess.get_state(chat_id)

    handlers = {
        "START":            handle_start,
        "GET_NAME":         handle_get_name,
        "GET_EMAIL":        handle_get_email,
        "GET_PHONE":        handle_get_phone,
        "GET_INSTAGRAM":    handle_get_instagram,
        "GET_OTHER_SOCIALS":handle_get_other_socials,
        "DISQUALIFIED":     handle_disqualified,
        "DONE":             handle_done,
    }

    handler = handlers.get(state)
    if handler:
        await handler(chat_id, text)
    else:
        # States like REVIEWING, ROUTING are async — ignore texts during them
        send_message(chat_id, "⏳ Please wait while we process your information...")


# ── Entry point — called on every button tap (callback query) ────────────────

async def handle_callback(chat_id: int, callback_data: str, message_id: int):
    """Routes inline keyboard button taps."""
    state = sess.get_state(chat_id)

    if state == "GET_MONETIZATION":
        await handle_monetization_callback(chat_id, callback_data, message_id)
    elif state == "GET_GOALS":
        await handle_goals_callback(chat_id, callback_data, message_id)


# ── STATE: START ──────────────────────────────────────────────────────────────

async def handle_start(chat_id: int, text: str = ""):
    sess.set_state(chat_id, "GET_NAME")
    send_message(
        chat_id,
        "👋 <b>Welcome to Unruly!</b>\n\n"
        "We help creators grow their income and reach. "
        "This quick application takes about 2 minutes.\n\n"
        "Let's start with the basics! What's your <b>full name</b>?"
    )


# ── STATE: GET_NAME ───────────────────────────────────────────────────────────

async def handle_get_name(chat_id: int, text: str):
    name = text.strip()

    if len(name) < 2:
        send_message(chat_id, "Please enter your full name (first and last).")
        return

    sess.save_field(chat_id, "name", name)
    sess.set_state(chat_id, "GET_EMAIL")

    send_message(
        chat_id,
        f"Nice to meet you, <b>{name}</b>! 🙌\n\n"
        f"What's your <b>email address</b>?"
    )


# ── STATE: GET_EMAIL ──────────────────────────────────────────────────────────

# app/handlers/flow.py

async def handle_get_email(chat_id: int, text: str):
    email = text.strip().lower()
    result = validate_email(email)

    if not result["valid"]:
        send_message(chat_id, f"❌ {result['reason']}\n\nPlease enter your email again:")
        return

    sess.save_field(chat_id, "email", result.get("normalized", email))
    sess.set_state(chat_id, "GET_PHONE")

    send_message(
        chat_id,
        "Got it! ✅\n\nWhat's your <b>phone number</b>?\n"
        "<i>Include your country code, e.g. +1 555 123 4567</i>"
    )


# ── STATE: GET_PHONE ──────────────────────────────────────────────────────────

async def handle_get_phone(chat_id: int, text: str):
    phone = text.strip()
    result = validate_phone(phone)

    if not result["valid"]:
        send_message(chat_id, f"❌ {result['reason']}\n\nPlease enter your phone number again:")
        return

    sess.save_field(chat_id, "phone", result.get("normalized", phone))
    sess.set_state(chat_id, "GET_INSTAGRAM")

    send_message(
        chat_id,
        "Perfect! 📱\n\nWhat's your <b>Instagram handle</b>?\n"
        "<i>e.g. @yourhandle or yourhandle</i>"
    )


# ── STATE: GET_INSTAGRAM ──────────────────────────────────────────────────────

async def handle_get_instagram(chat_id: int, text: str):
    result = validate_instagram(text)

    if not result["valid"]:
        send_message(chat_id, f"❌ {result['reason']}")
        return

    handle = result["handle"]
    sess.save_field(chat_id, "instagram", handle)
    sess.set_state(chat_id, "GET_OTHER_SOCIALS")

    send_message(
        chat_id,
        f"Great, @{handle}! 📸\n\n"
        f"Do you have any other social media profiles?\n"
        f"<i>TikTok, Snapchat, YouTube, X — share any links you'd like us to see.</i>\n\n"
        f"Or type <b>skip</b> if Instagram is your main platform."
    )


# ── STATE: GET_OTHER_SOCIALS ──────────────────────────────────────────────────

async def handle_get_other_socials(chat_id: int, text: str):
    other = None if text.strip().lower() == "skip" else text.strip()
    sess.save_field(chat_id, "other_socials", other)

    # Now pull Instagram metrics
    await handle_reviewing(chat_id)


# ── STATE: REVIEWING ──────────────────────────────────────────────────────────

async def handle_reviewing(chat_id: int, text: str = ""):
    sess.set_state(chat_id, "REVIEWING")
    send_typing(chat_id)

    instagram = sess.get_data(chat_id).get("instagram")
    send_message(
        chat_id,
        f"⏳ Give me a moment while I review your profile <b>@{instagram}</b>..."
    )

    # Pull metrics from RapidAPI
    metrics = get_metrics(instagram)

    if not metrics["found"]:
        send_message(
            chat_id,
            f"⚠️ I couldn't find the Instagram profile <b>@{instagram}</b>.\n\n"
            f"Please double-check your handle and try again:"
        )
        sess.set_state(chat_id, "GET_INSTAGRAM")
        return

    # Save all metrics to session
    sess.save_field(chat_id, "followers",       metrics["followers"])
    sess.save_field(chat_id, "avg_likes",       metrics["avg_likes"])
    sess.save_field(chat_id, "avg_comments",    metrics["avg_comments"])
    sess.save_field(chat_id, "engagement_rate", metrics["engagement_rate"])

    # Run qualification check
    qualification = qualify_creator(metrics, MIN_FOLLOWERS, MIN_AVG_LIKES)
    sess.save_field(chat_id, "qualified", qualification["qualified"])

    if not qualification["qualified"]:
        sess.set_state(chat_id, "DISQUALIFIED")
        send_message(chat_id, qualification["message"])
        return

    # Qualified — show their stats and continue
    send_message(
        chat_id,
        f"✅ <b>Profile verified!</b>\n\n"
        f"👥 <b>Followers:</b> {metrics['followers']:,}\n"
        f"❤️ <b>Avg Likes:</b> {metrics['avg_likes']:,}\n"
        f"💬 <b>Avg Comments:</b> {metrics['avg_comments']:,}\n"
        f"📊 <b>Engagement Rate:</b> {metrics['engagement_rate']}%\n\n"
        f"Looking great! Let's keep going 🚀"
    )

    # Move to monetization
    sess.set_state(chat_id, "GET_MONETIZATION")
    send_inline_keyboard(
        chat_id,
        "💰 <b>How do you currently monetize your content?</b>\n"
        "<i>Select all that apply, then tap Continue.</i>",
        monetization_keyboard()
    )


# ── STATE: GET_MONETIZATION (button taps) ────────────────────────────────────

async def handle_monetization_callback(chat_id: int, callback_data: str, message_id: int):
    session  = sess.get_session(chat_id)
    selected = session["pending_selections"]["monetization"]

    if callback_data == "mon_done":
        if not selected:
            send_message(chat_id, "Please select at least one option before continuing.")
            return

        # Save human-readable labels
        labels = [MONETIZATION_LABELS.get(v, v) for v in selected]
        sess.save_field(chat_id, "monetization", labels)
        session["pending_selections"]["monetization"] = []

        sess.set_state(chat_id, "GET_GOALS")
        send_inline_keyboard(
            chat_id,
            "🎯 <b>What are you looking for?</b>\n"
            "<i>Select all that apply, then tap Continue.</i>",
            goals_keyboard()
        )
        return

    # Toggle selection
    if callback_data in selected:
        selected.remove(callback_data)
    else:
        selected.append(callback_data)

    session["pending_selections"]["monetization"] = selected

    # Update keyboard to show checkmarks
    from app.services.telegram import edit_message_reply_markup
    edit_message_reply_markup(chat_id, message_id, monetization_keyboard(selected))


# ── STATE: GET_GOALS (button taps) ───────────────────────────────────────────

async def handle_goals_callback(chat_id: int, callback_data: str, message_id: int):
    session  = sess.get_session(chat_id)
    selected = session["pending_selections"]["goals"]

    if callback_data == "goal_done":
        if not selected:
            send_message(chat_id, "Please select at least one option before continuing.")
            return

        labels = [GOALS_LABELS.get(v, v) for v in selected]
        sess.save_field(chat_id, "goals", labels)
        session["pending_selections"]["goals"] = []

        # Route to TA team
        await handle_routing(chat_id)
        return

    # Toggle selection
    if callback_data in selected:
        selected.remove(callback_data)
    else:
        selected.append(callback_data)

    session["pending_selections"]["goals"] = selected

    from app.services.telegram import edit_message_reply_markup
    edit_message_reply_markup(chat_id, message_id, goals_keyboard(selected))


# ── STATE: ROUTING ────────────────────────────────────────────────────────────

async def handle_routing(chat_id: int, text: str = ""):
    from datetime import datetime
    sess.set_state(chat_id, "ROUTING")

    data = sess.get_data(chat_id)

    # Assign TA member
    ta_handle = assign_ta()
    sess.save_field(chat_id, "assigned_ta",    ta_handle)
    sess.save_field(chat_id, "date_submitted", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))

    send_typing(chat_id)

    # Send intro message to creator
    intro = build_intro_message(data, ta_handle)
    send_message(chat_id, intro)

    # TODO Phase 3: save to Google Sheets + Monday CRM
    # TODO Phase 3: send Slack alert to internal team
    # TODO Phase 3: send TA alert message

    sess.set_state(chat_id, "DONE")


# ── STATE: DISQUALIFIED ───────────────────────────────────────────────────────

async def handle_disqualified(chat_id: int, text: str = ""):
    send_message(
        chat_id,
        "We've saved your information and will reach out if the right opportunity comes up. 💛\n\n"
        "In the meantime, keep creating! Type /start if you'd like to reapply in the future."
    )


# ── STATE: DONE ───────────────────────────────────────────────────────────────

async def handle_done(chat_id: int, text: str = ""):
    send_message(
        chat_id,
        "Your application is already submitted! 🎉\n\n"
        "Your talent acquisition contact will be in touch soon.\n"
        "Type /start if you'd like to submit a new application."
    )
