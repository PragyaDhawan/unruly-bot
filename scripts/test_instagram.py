"""
scripts/test_instagram.py
Run this to verify your RapidAPI key and Instagram metrics work correctly.

Usage:
    python scripts/test_instagram.py cristiano
    python scripts/test_instagram.py YOUR_TEST_HANDLE
"""

import sys
import json
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.social_metrics import get_metrics, qualify_creator

def test(username: str):
    print(f"\n🔍 Looking up @{username}...\n")

    metrics = get_metrics(username)

    if not metrics["found"]:
        print(f"❌ Not found: {metrics['error']}")
        return

    print("✅ Profile found!\n")
    print(f"  👤 Name:            {metrics['full_name']}")
    print(f"  📸 Username:        @{metrics['username']}")
    print(f"  👥 Followers:       {metrics['followers']:,}")
    print(f"  ❤️  Avg Likes:       {metrics['avg_likes']:,}")
    print(f"  💬 Avg Comments:    {metrics['avg_comments']:,}")
    print(f"  📊 Engagement Rate: {metrics['engagement_rate']}%")
    print(f"  ✔️  Verified:        {metrics['is_verified']}")
    print(f"  🏢 Business:        {metrics['is_business']}")
    print(f"  🔗 Profile URL:     {metrics['profile_url']}")

    print("\n── Qualification Check ──────────────────")
    result = qualify_creator(metrics)
    status = "✅ QUALIFIED" if result["qualified"] else "❌ NOT QUALIFIED"
    print(f"  {status}")
    if result["message"]:
        print(f"  Message: {result['message']}")

    print("\n── Raw Metrics JSON ─────────────────────")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    handle = sys.argv[1] if len(sys.argv) > 1 else "cristiano"
    test(handle)
