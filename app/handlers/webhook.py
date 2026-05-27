"""
app/handlers/webhook.py
Telegram webhook receiver — Phase 2 will build this out fully.
This file is a placeholder so the app starts successfully in Phase 1.
"""

from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhook")
async def telegram_webhook(req: Request):
    """
    Receives all incoming Telegram messages.
    Full implementation coming in Phase 2.
    """
    data = await req.json()
    print(f"📩 Incoming update: {data}")
    return {"ok": True}
