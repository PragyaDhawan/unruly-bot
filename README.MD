# Unruly Talent Bot

AI-powered Telegram onboarding chatbot for creator qualification, lead routing, and submission tracking.

---

# Features

- Telegram onboarding flow
- Email + phone validation
- Instagram social metric lookup
- Creator qualification logic
- Google Sheets lead tracking
- Automated TA assignment
- Internal Telegram routing alerts
- Creator handoff messaging

---

# Tech Stack

- FastAPI
- Telegram Bot API
- RapidAPI (Instagram metrics)
- AbstractAPI (email + phone validation)
- Google Sheets API
- Python

---

# Project Structure

```bash
app/
 ├── handlers/
 ├── services/
 ├── utils/
config/
scripts/
main.py
```

---

# Setup

## Clone Project

```bash
git clone <repo>
cd unruly-bot-phase1
```

## Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create `.env`

```env
TELEGRAM_BOT_TOKEN=
OPENAI_API_KEY=
RAPIDAPI_KEY=

ABSTRACT_EMAIL_API_KEY=
ABSTRACT_PHONE_API_KEY=

GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json
GOOGLE_SHEET_ID=

TA_MEMBERS=@ta_member1,@ta_member2
TA_GROUP_CHAT_ID=

SKIP_EXTERNAL_VALIDATION=false
SKIP_QUALIFICATION=false
```

---

# Telegram Bot Setup

## Create Bot

- Open BotFather
- Run `/newbot`
- Copy bot token

## Register Webhook

```bash
python scripts/register_webhook.py --url https://your-ngrok-url.ngrok-free.app
```

---

# Google Sheets Setup

## Enable Google Sheets API

- Create Google Cloud project
- Enable Google Sheets API
- Create Service Account
- Download JSON credentials

## Share Spreadsheet

Share Google Sheet with your service account email and grant Editor access.

---

# Internal TA Routing Setup

## Create Telegram Group

Example:
```text
Unruly Talent Routing
```

Add:
- bot
- internal team members

## Get Group Chat ID

Add temporary webhook log:

```python
print(data)
```

Copy:

```json
"chat": {
  "id": -5229522585
}
```

Add to `.env`

```env
TA_GROUP_CHAT_ID=-5229522585
```

---

# Qualification Logic

Defined in:

```python
config/settings.py
```

```python
MIN_FOLLOWERS = 10000
MIN_AVG_LIKES = 1000
```

Creator is disqualified only if BOTH:
- followers < threshold
- avg likes < threshold

---

# Lead Routing Flow

1. Creator completes onboarding
2. Instagram metrics are fetched
3. Creator is qualified/disqualified
4. Submission saved to Google Sheets
5. TA assigned using round-robin routing
6. Internal Telegram group receives handoff alert
7. Creator receives handoff message

---

# Google Sheets Tracking

Stored fields:
- name
- email
- phone
- Instagram
- followers
- avg likes
- engagement rate
- monetization
- goals
- qualification status
- assigned TA
- date submitted
- call status

---

# Run Application

```bash
uvicorn main:app --reload --port 8000
```

---

# Testing

## Qualified Flow

```env
SKIP_QUALIFICATION=true
```

## Validation Bypass

```env
SKIP_EXTERNAL_VALIDATION=true
```

---

# Future Improvements

- Monday CRM integration
- Slack notifications
- Redis session persistence
- Admin dashboard
- Scheduling integrations