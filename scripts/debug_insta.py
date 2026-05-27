"""
scripts/debug_instagram.py
Tests the correct API endpoints and prints raw responses.

Usage:
    python scripts/debug_instagram.py kendalljenner
"""

import sys, json, os, requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

RAPIDAPI_KEY  = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "instagram-best-experience.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
    "Content-Type":    "application/json",
}

def try_endpoint(label, path, params):
    url = f"https://{RAPIDAPI_HOST}/{path}"
    print(f"\n{'='*60}")
    print(f"TESTING: {label}")
    print(f"URL: {url}")
    print(f"PARAMS: {params}")
    print(f"{'='*60}")
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        data = r.json()
        print(json.dumps(data, indent=2)[:2000])
        return data
    except Exception as e:
        print(f"ERROR: {e}")
        return {}

def debug(username: str):
    username = username.lstrip("@").strip()
    print(f"\n🔍 Debugging @{username}")

    # ── 1. Try all known user_id endpoint variations ──────────────────────────
    uid_result = try_endpoint(
        "user_id_by_username (from curl)",
        "user_id_by_username",
        {"username": username}
    )

    # Extract user_id from result
    user_id = (
        uid_result.get("UserID")
        or uid_result.get("user_id")
        or uid_result.get("id")
        or uid_result.get("data", {}).get("id")
    )
    print(f"\n✅ Resolved user_id: {user_id}")

    # ── 2. Try all known profile endpoint variations ───────────────────────────
    for path, params in [
        ("profile_by_username",       {"username": username}),
        ("user_profile_by_username",  {"username": username}),
        ("profile",                   {"username": username}),
        ("get_profile",               {"username": username}),
    ]:
        result = try_endpoint(f"Profile: /{path}", path, params)
        # Check if we got real data (not an error message)
        if "message" not in result or "does not exist" not in str(result.get("message","")):
            print(f"\n✅ WORKING PROFILE ENDPOINT: /{path}")
            print("Keys:", list(result.keys()) if isinstance(result, dict) else type(result))
            break

    # ── 3. Try all known feed endpoint variations ──────────────────────────────
    if user_id:
        for path, params in [
            ("feed",                  {"user_id": user_id}),
        ]:
            result = try_endpoint(f"Feed: /{path}", path, params)
            if "message" not in result or "does not exist" not in str(result.get("message","")):
                print(f"\n✅ WORKING FEED ENDPOINT: /{path}")
                items = result.get("items", result.get("data", []))
                if isinstance(items, list) and items:
                    print("First post keys:", list(items[0].keys()))
                    for k, v in items[0].items():
                        if any(w in k.lower() for w in ["like","comment","play","view"]):
                            print(f"  {k}: {v}")
                break

if __name__ == "__main__":
    handle = sys.argv[1] if len(sys.argv) > 1 else "kendalljenner"
    debug(handle)