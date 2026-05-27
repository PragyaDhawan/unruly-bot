"""
scripts/register_webhook.py
Run this once after deployment to tell Telegram where to send messages.

Usage:
    python scripts/register_webhook.py --url https://your-app.railway.app

Requirements:
    - TELEGRAM_BOT_TOKEN must be set in your .env
"""

import sys
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def register_webhook(app_url: str):
    webhook_url = f"{app_url.rstrip('/')}/webhook"
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

    print(f"📡 Registering webhook: {webhook_url}")

    response = requests.post(api_url, json={"url": webhook_url})
    result = response.json()

    if result.get("ok"):
        print(f"✅ Webhook registered successfully!")
        print(f"   URL: {webhook_url}")
    else:
        print(f"❌ Failed to register webhook:")
        print(f"   {result}")

def check_webhook():
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    response = requests.get(api_url)
    print("\n📋 Current webhook info:")
    print(response.json())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/register_webhook.py --url https://your-app.railway.app")
        print("       python scripts/register_webhook.py --check")
        sys.exit(1)

    if sys.argv[1] == "--check":
        check_webhook()
    elif sys.argv[1] == "--url" and len(sys.argv) == 3:
        register_webhook(sys.argv[2])
    else:
        print("Invalid arguments. Use --url <your_app_url> or --check")
