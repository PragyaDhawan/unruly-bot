"""
main.py
Entry point for the Unruly Talent Bot.
Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from config.settings import validate_config, PORT
from app.handlers.webhook import router as webhook_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup
    print("🚀 Unruly Talent Bot starting up...")
    validate_config()
    yield
    # Runs once on shutdown
    print("👋 Bot shutting down.")

app = FastAPI(
    title="Unruly Talent Bot",
    description="Telegram chatbot for talent acquisition intake",
    version="1.0.0",
    lifespan=lifespan
)

# Register routes
app.include_router(webhook_router)

@app.get("/")
async def health_check():
    return {"status": "running", "bot": "Unruly Talent Bot v1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
