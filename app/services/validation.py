import re
import requests
import os
from dotenv import load_dotenv

load_dotenv()

ABSTRACT_EMAIL_API_KEY = os.getenv("ABSTRACT_EMAIL_API_KEY")
ABSTRACT_PHONE_API_KEY = os.getenv("ABSTRACT_PHONE_API_KEY")

EMAIL_REGEX = re.compile(r'^[\w.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$')
PHONE_REGEX = re.compile(r'^\+?[\d\s\-\(\)]{7,25}$')


def validate_email(email: str) -> dict:
    email = email.strip().lower()

    if not EMAIL_REGEX.match(email):
        return {"valid": False, "reason": "That doesn't look like a valid email address.", "normalized": email}

    if not ABSTRACT_EMAIL_API_KEY:
        return {"valid": True, "reason": "ok", "normalized": email}
    print(f"[validation] Calling Abstract email API for: {email}")
    try:
        r = requests.get(
            "https://emailreputation.abstractapi.com/v1/",
            params={
                "api_key": ABSTRACT_EMAIL_API_KEY,
                "email": email,
            },
            timeout=10,
        )
        print(f"[validation] Abstract email status: {r.status_code}")
        print(f"[validation] Abstract email response: {r.text[:500]}")
        r.raise_for_status()
        data = r.json()

        deliverability = data.get("email_deliverability", {})
        quality = data.get("email_quality", {})

        is_valid = (
            deliverability.get("status") == "deliverable"
            and deliverability.get("is_format_valid", False)
            and deliverability.get("is_mx_valid", False)
            and deliverability.get("is_smtp_valid", False)
            and not quality.get("is_disposable", False)
        )

        if not is_valid:
            return {
                "valid": False,
                "reason": "That email address doesn't appear to be valid. Please double-check it.",
                "normalized": data.get("email_address", email),
                "raw": data,
            }

        return {
            "valid": True,
            "reason": "ok",
            "normalized": data.get("email_address", email),
            "raw": data,
        }

    except Exception as e:
        print(f"[validation] Abstract email error: {e}")
        return {"valid": True, "reason": "ok", "normalized": email}


def validate_phone(phone: str) -> dict:
    raw = phone.strip()

    if not PHONE_REGEX.match(raw):
        return {"valid": False, "reason": "That doesn't look like a valid phone number. Please include your country code.", "normalized": raw}

    if not ABSTRACT_PHONE_API_KEY:
        return {"valid": True, "reason": "ok", "normalized": raw}
    print(f"[validation] Calling Abstract phone API for: {raw}")
    try:
        r = requests.get(
            "https://phoneintelligence.abstractapi.com/v1/",
            params={
                "api_key": ABSTRACT_PHONE_API_KEY,
                "phone": raw.lstrip("+"),
            },
            timeout=10,
        )
        print(f"[validation] Abstract phone status: {r.status_code}")
        print(f"[validation] Abstract phone response: {r.text[:500]}")
        r.raise_for_status()
        data = r.json()

        if not data.get("phone_validation", {}).get("is_valid", False):
            return {
                "valid": False,
                "reason": "That phone number doesn't appear to be valid. Please check and try again.",
                "normalized": raw,
                "raw": data,
            }

        return {
            "valid": True,
            "reason": "ok",
            "normalized": data.get("phone_format", {}).get("international", raw),
            "raw": data,
        }

    except Exception as e:
        print(f"[validation] Abstract phone error: {e}")
        return {"valid": True, "reason": "ok", "normalized": raw}
    
def sanitize_instagram(handle: str) -> str:
    """Strips @ and URLs, returns clean handle."""
    handle = handle.strip()

    # Remove URL patterns like https://instagram.com/handle
    handle = re.sub(
        r'https?://(www\.)?instagram\.com/',
        '',
        handle
    )

    handle = handle.lstrip('@').strip().rstrip('/')
    return handle


def validate_instagram(handle: str) -> dict:
    """Basic check that handle looks valid."""
    clean = sanitize_instagram(handle)

    if not clean:
        return {
            "valid": False,
            "reason": "Please enter your Instagram username."
        }

    if not re.match(r'^[\w\.]{1,30}$', clean):
        return {
            "valid": False,
            "reason": (
                "That doesn't look like a valid Instagram handle. "
                "Please try again (e.g. @yourhandle)."
            )
        }

    return {
        "valid": True,
        "reason": "ok",
        "handle": clean
    }