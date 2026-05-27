"""
app/handlers/webhook.py
Receives all incoming Telegram updates and routes them to flow.py.

Two types of updates:
  1. message        — user typed something
  2. callback_query — user tapped an inline button
"""

from fastapi import APIRouter, Request
from app.handlers.flow import handle_message, handle_callback
from app.services.telegram import answer_callback_query

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    # ── Inline button tap ─────────────────────────────────────────────────────
    if "callback_query" in data:
        cq            = data["callback_query"]
        chat_id       = cq["message"]["chat"]["id"]
        message_id    = cq["message"]["message_id"]
        callback_data = cq.get("data", "")
        cq_id         = cq["id"]

        # Always acknowledge to remove loading spinner on button
        answer_callback_query(cq_id)

        await handle_callback(chat_id, callback_data, message_id)
        return {"ok": True}

    # ── Regular text message ──────────────────────────────────────────────────
    if "message" in data:
        message = data["message"]

        # Ignore non-text updates (photos, stickers, voice, etc.)
        if "text" not in message:
            return {"ok": True}

        chat_id = message["chat"]["id"]
        text    = message.get("text", "")

        await handle_message(chat_id, text)
        return {"ok": True}

    return {"ok": True}
