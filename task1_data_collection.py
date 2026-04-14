"""
TrendPulse — Task 1: Fetch Data from HackerNews API
====================================================
Fetches the top 500 HackerNews story IDs, assigns each story to one of
5 categories based on keyword matching in the title, collects up to 25
stories per category (125 total), and saves them to a dated JSON file.

Author : Obilisetti Ravi Kiran
"""

from __future__ import annotations

import requests
import json
import os
import time
import urllib3
from datetime import datetime

# Suppress SSL warnings caused by corporate proxy certificate interception
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── API endpoints ──────────────────────────────────────────────────────────────
TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL        = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

# Add User-Agent header as required by the assignment
HEADERS = {"User-Agent": "TrendPulse/1.0"}

# ── Category keyword mapping (case-insensitive matching) ──────────────────────
# Extra keywords added to science and sports to improve coverage on HackerNews
# (those categories are naturally sparse on a tech-focused platform).
CATEGORIES = {
    "technology":    ["ai", "software", "tech", "code", "computer", "data",
                      "cloud", "api", "gpu", "llm"],
    "worldnews":     ["war", "government", "country", "president", "election",
                      "climate", "attack", "global"],
    "sports":        ["nfl", "nba", "fifa", "sport", "game", "team", "player",
                      "league", "championship", "olympic", "tournament", "athlete"],
    "science":       ["research", "study", "space", "physics", "biology",
                      "discovery", "nasa", "genome", "medicine", "quantum",
                      "experiment", "universe", "planet", "cancer", "vaccine"],
    "entertainment": ["movie", "film", "music", "netflix", "game", "book",
                      "show", "award", "streaming"],
}

MAX_PER_CATEGORY = 25   # collect up to 25 stories per category
MAX_IDS          = 500  # HackerNews topstories returns ~500 IDs — take all of them


def assign_category(title: str) -> str | None:
    """
    Check the story title against each category's keywords.
    Returns the first matching category name, or None if no match.
    """
    title_lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category
    return None  # story doesn't fit any category


def fetch_top_story_ids() -> list[int]:
    """
    Fetch the list of top story IDs from HackerNews.
    Returns the first MAX_IDS ids, or an empty list if the request fails.
    """
    print("Fetching top story IDs...")
    try:
        response = requests.get(TOP_STORIES_URL, headers=HEADERS, timeout=10, verify=False)
        response.raise_for_status()
        all_ids = response.json()
        print(f"  Retrieved {len(all_ids)} total story IDs. Using first {MAX_IDS}.")
        return all_ids[:MAX_IDS]
    except requests.RequestException as e:
        print(f"  [ERROR] Failed to fetch story IDs: {e}")
        return []


def fetch_story(story_id: int) -> dict | None:
    """
    Fetch a single story's details by its ID.
    Returns the story dict, or None if the request fails or the item has no title.
    """
    try:
        url = ITEM_URL.format(id=story_id)
        response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        response.raise_for_status()
        story = response.json()
        # Skip deleted/dead stories and items without a title (e.g. comments)
        if story and story.get("title") and not story.get("dead") and not story.get("deleted"):
            return story
    except requests.RequestException as e:
        print(f"  [WARN] Could not fetch story {story_id}: {e}")
    return None


def collect_stories(story_ids: list[int]) -> list[dict]:
    """
    Two-pass approach:
      Pass 1 — Fetch every story's details from the API (up to MAX_IDS stories).
      Pass 2 — Loop over each category, pick up to MAX_PER_CATEGORY matching
               stories, and sleep 2 seconds between categories (one sleep per
               category loop, not per individual story fetch).
    """
    # ── Pass 1: fetch raw story data from the API ──────────────────────────
    print(f"Fetching details for up to {len(story_ids)} stories...")
    raw_stories: list[dict] = []
    for story_id in story_ids:
        story = fetch_story(story_id)
        if story:
            raw_stories.append(story)
    print(f"  Got {len(raw_stories)} valid stories.\n")

    # ── Pass 2: assign stories to categories, one sleep between categories ──
    collected: list[dict] = []
    now = datetime.now().isoformat(timespec="seconds")
    category_names = list(CATEGORIES.keys())

    for idx, category in enumerate(category_names):
        count = 0
        print(f"Processing category: '{category}'")

        for story in raw_stories:
            if count >= MAX_PER_CATEGORY:
                break  # this category is full

            title = story.get("title", "")
            # Only take stories that belong to the current category
            if assign_category(title) != category:
                continue

            # Extract the 7 required fields
            record = {
                "post_id":      story.get("id"),
                "title":        title,
                "category":     category,
                "score":        story.get("score", 0),
                "num_comments": story.get("descendants", 0),
                "author":       story.get("by", "unknown"),
                "collected_at": now,
            }
            collected.append(record)
            count += 1

        print(f"  Collected {count} stories for '{category}'.")

        # Sleep 2 seconds between categories — but not after the last one
        if idx < len(category_names) - 1:
            print("  Sleeping 2 seconds before next category...")
            time.sleep(2)

    return collected


def save_to_json(stories: list[dict]) -> str:
    """
    Create the data/ folder if needed and save stories to a dated JSON file.
    Returns the output file path.
    """
    os.makedirs("data", exist_ok=True)  # create data/ folder if it doesn't exist
    date_str  = datetime.now().strftime("%Y%m%d")
    file_path = f"data/trends_{date_str}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2, ensure_ascii=False)

    return file_path


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Step 1: Get top story IDs
    story_ids = fetch_top_story_ids()
    if not story_ids:
        print("No story IDs retrieved. Exiting.")
        exit(1)

    # Step 2: Fetch stories and extract required fields
    print("\nFetching and categorising stories...")
    stories = collect_stories(story_ids)

    # Step 3: Save to JSON file
    output_path = save_to_json(stories)
    print(f"\nCollected {len(stories)} stories. Saved to {output_path}")
