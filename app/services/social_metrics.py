"""
app/services/social_metrics.py

Fetches Instagram metrics via RapidAPI "Instagram Best Experience" by Lobster.

Confirmed response structure from API docs:
  GET /v1/feed → { "items": [...], "num_results": 12, "status": "ok" }
  Each item → { "like_count": 1244018, "comment_count": 20499, ... }
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY  = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "instagram-best-experience.p.rapidapi.com"

BASE_HEADERS = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
    "Content-Type":    "application/json",
}


# ── 1. Get numeric user_id from username ──────────────────────────────────────

def get_user_id(username: str) -> str | None:
    """Converts @handle to numeric Instagram user_id."""
    username = username.lstrip("@").strip()
    try:
        r = requests.get(
            f"https://{RAPIDAPI_HOST}/user_id_by_username",
            headers=BASE_HEADERS,
            params={"username": username},
            timeout=10
        )
        data = r.json()
        user_id = data.get("UserID")
        return str(user_id) if user_id else None
    except Exception as e:
        print(f"[social_metrics] get_user_id error: {e}")
        return None


# ── 2. Get profile by username ────────────────────────────────────────────────

def get_profile(username: str) -> dict:
    """Returns profile data: follower_count, user id, bio, is_verified, etc."""
    username = username.lstrip("@").strip()
    try:
        r = requests.get(
            f"https://{RAPIDAPI_HOST}/profile",
            headers=BASE_HEADERS,
            params={"username": username},
            timeout=10
        )
        data = r.json()
        return data
    except Exception as e:
        print(f"[social_metrics] get_profile error: {e}")
        return {}


# ── 3. Get feed posts ─────────────────────────────────────────────────────────

def get_feed(user_id: str) -> list:
    """
    Calls GET /v1/feed with user_id.

    Confirmed response shape:
    {
      "items": [
        { "like_count": 1244018, "comment_count": 20499, ... },
        ...
      ],
      "num_results": 12,
      "more_available": true,
      "status": "ok"
    }

    Returns the items list directly.
    """
    try:
        r = requests.get(
            f"https://{RAPIDAPI_HOST}/feed",
            headers=BASE_HEADERS,
            params={"user_id": user_id},
            timeout=10
        )
        data = r.json()

        # "items" is at the top level per the confirmed API response
        posts = data.get("items", [])
        print(f"[social_metrics] Fetched {len(posts)} posts for user_id={user_id}")
        return posts

    except Exception as e:
        print(f"[social_metrics] get_feed error: {e}")
        return []


# ── 4. Compute engagement stats ───────────────────────────────────────────────

def compute_engagement(posts: list, follower_count: int) -> dict:
    """
    Averages like_count and comment_count across all posts.
    Confirmed field names from API: "like_count", "comment_count"
    """
    if not posts:
        return {"avg_likes": 0, "avg_comments": 0, "engagement_rate": 0.0}

    total_likes    = sum(p.get("like_count",    0) for p in posts)
    total_comments = sum(p.get("comment_count", 0) for p in posts)
    count          = len(posts)

    avg_likes    = round(total_likes    / count)
    avg_comments = round(total_comments / count)

    engagement_rate = 0.0
    if follower_count > 0:
        engagement_rate = round(
            ((total_likes + total_comments) / count / follower_count) * 100, 2
        )

    return {
        "avg_likes":       avg_likes,
        "avg_comments":    avg_comments,
        "engagement_rate": engagement_rate,
    }


# ── MASTER FUNCTION ───────────────────────────────────────────────────────────

def get_metrics(username: str) -> dict:
    """
    Pass an Instagram username (with or without @).
    Returns a single clean dict with everything needed for qualification.

    Example return:
    {
        "found":            True,
        "username":         "nike",
        "full_name":        "Nike",
        "followers":        250000000,
        "following":        200,
        "post_count":       1500,
        "avg_likes":        450000,
        "avg_comments":     12000,
        "engagement_rate":  1.85,
        "is_verified":      True,
        "is_business":      True,
        "biography":        "Just Do It.",
        "profile_url":      "https://instagram.com/nike",
        "error":            None
    }
    """
    username = username.lstrip("@").strip()

    empty = {
        "found":           False,
        "username":        username,
        "full_name":       None,
        "followers":       0,
        "following":       0,
        "post_count":      0,
        "avg_likes":       0,
        "avg_comments":    0,
        "engagement_rate": 0.0,
        "is_verified":     False,
        "is_business":     False,
        "biography":       None,
        "profile_url":     f"https://instagram.com/{username}",
        "error":           None,
    }

    # Step 1 — Profile
    profile = get_profile(username)
    print("[social_metrics] profile:", profile)
    print("[social_metrics] follower_count raw:", profile.get("follower_count"))
    # print("[social_metrics] keys:", list(profile.keys()))
    if not profile:
        empty["error"] = "Instagram profile not found. Please double-check the handle."
        return empty

    follower_count = (
        profile.get("follower_count")
        # or profile.get("followers_count")
        # or profile.get("edge_followed_by", {}).get("count", 0)
        # or 0
    )

    # Step 2 — Resolve user_id (profile usually includes id or pk)
    user_id = str(
        # profile.get("id")
        profile.get("pk")
        # or get_user_id(username)
        # or ""
    )

    # Step 3 — Feed for avg likes/comments
    posts      = get_feed(user_id) if user_id else []
    engagement = compute_engagement(posts, follower_count)

    return {
        "found":           True,
        "username":        profile.get("username", username),
        "full_name":       profile.get("full_name") or profile.get("name"),
        "followers":       follower_count,
        "following":       profile.get("following_count") or profile.get("following", 0),
        "post_count":      profile.get("media_count") or profile.get("post_count", 0),
        "avg_likes":       engagement["avg_likes"],
        "avg_comments":    engagement["avg_comments"],
        "engagement_rate": engagement["engagement_rate"],
        "is_verified":     profile.get("is_verified", False),
        "is_business":     profile.get("is_business_account", False),
        "biography":       profile.get("biography") or profile.get("bio"),
        "profile_url":     f"https://instagram.com/{profile.get('username', username)}",
        "error":           None,
    }


# ── QUALIFICATION CHECK ───────────────────────────────────────────────────────

def qualify_creator(metrics: dict, min_followers: int = 10_000, min_avg_likes: int = 1_000) -> dict:
    """
    Disqualifies only if BOTH followers AND avg_likes are below threshold.
    Matching the spec: 'under 10K followers AND under 1K average likes'
    """
    if not metrics["found"]:
        return {
            "qualified": False,
            "reason":    "profile_not_found",
            "message":   "We couldn't find that Instagram profile. Please double-check the handle.",
        }

    below_followers = metrics["followers"] < min_followers
    below_likes     = metrics["avg_likes"] < min_avg_likes

    if below_followers and below_likes:
        return {
            "qualified": False,
            "reason":    "below_threshold",
            "message": (
                "Thank you so much for your inquiry. Based on your current socials, "
                "we may not have the right opportunity available at this time, but "
                "we'll keep your information on file and reach back out if something "
                "aligns in the future. 💛"
            ),
        }

    return {
        "qualified": True,
        "reason":    "meets_threshold",
        "message":   None,
    }
