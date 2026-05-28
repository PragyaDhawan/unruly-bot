"""
main.py
Entry point for the Unruly Talent Bot.
Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from config.settings import PORT
from app.handlers.webhook import router as webhook_router
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Unruly Talent Bot starting up...")

    # Phase 2 required keys
    phase2_required = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "OPENAI_API_KEY":     os.getenv("OPENAI_API_KEY"),
        "RAPIDAPI_KEY":       os.getenv("RAPIDAPI_KEY"),
    }

    # Phase 3 keys (optional for now)
    phase3_optional = {
        # "ABSTRACT_API_KEY":  os.getenv("ABSTRACT_API_KEY"),
        "GOOGLE_SHEET_ID":   os.getenv("GOOGLE_SHEET_ID"),
    }

    missing_required = [k for k, v in phase2_required.items() if not v]
    missing_optional = [k for k, v in phase3_optional.items() if not v]

    if missing_required:
        print("❌ MISSING REQUIRED KEYS — Bot will not work:")
        for k in missing_required:
            print(f"   ✗ {k}")
    else:
        print("✅ All Phase 2 keys loaded.")

    if missing_optional:
        print("⚠️  Phase 3 keys not set yet (OK for now):")
        for k in missing_optional:
            print(f"   ○ {k}")

    yield
    print("👋 Bot shutting down.")


app = FastAPI(
    title="Unruly Talent Bot",
    description="Telegram chatbot for talent acquisition intake",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(webhook_router)


@app.get("/")
async def health_check():
    return {"status": "running", "bot": "Unruly Talent Bot v2.0"}
