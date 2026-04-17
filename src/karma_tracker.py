import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

API_URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/user/{user_id}.json"
PROFILE_URL_TEMPLATE = "https://news.ycombinator.com/user?id={user_id}"
DEFAULT_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
HTML_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    )
}


def fetch_url(url: str, session: Optional[requests.Session] = None, **kwargs) -> requests.Response:
    """Fetch a URL with a few retries to tolerate transient upstream failures."""
    client = session or requests
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.get(url, timeout=DEFAULT_TIMEOUT_SECONDS, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            print(f"Request attempt {attempt}/{MAX_RETRIES} failed for {url}: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(attempt)

    raise last_error


def get_karma_from_api(user_id, session: Optional[requests.Session] = None):
    """Fetch karma points from the official Hacker News Firebase API."""
    url = API_URL_TEMPLATE.format(user_id=user_id)
    response = fetch_url(url, session=session, headers={"Accept": "application/json"})

    try:
        payload = response.json()
    except ValueError as exc:
        print(f"Failed to decode API response as JSON: {exc}")
        return None

    if not isinstance(payload, dict):
        print(f"Unexpected API response type: {type(payload).__name__}")
        return None

    karma_value = payload.get("karma")
    if isinstance(karma_value, int):
        print("Fetched karma from Hacker News API")
        return karma_value

    print(f"API response did not include an integer karma value: {payload!r}")
    return None


def get_karma_from_html(user_id, session: Optional[requests.Session] = None):
    """Fallback HTML scraper for cases where the API is unavailable."""
    url = PROFILE_URL_TEMPLATE.format(user_id=user_id)
    response = fetch_url(url, session=session, headers=HTML_HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    karma_row = soup.find("td", string=lambda value: value and value.strip() == "karma:")
    if not karma_row:
        body_prefix = response.text[:200].replace("\n", " ").strip()
        print(f"Could not find karma row in HTML. Response prefix: {body_prefix!r}")
        return None

    karma_value = karma_row.find_next_sibling("td").get_text(strip=True)
    try:
        print("Fetched karma from Hacker News profile HTML fallback")
        return int(karma_value)
    except ValueError:
        print(f"Failed to convert karma value '{karma_value}' to integer")
        return None


def get_karma(user_id, session: Optional[requests.Session] = None):
    """Fetch karma points for a given user from Hacker News."""
    try:
        karma = get_karma_from_api(user_id, session=session)
        if karma is not None:
            return karma
    except requests.RequestException as exc:
        print(f"API request failed: {exc}")

    print("Falling back to HTML scraping")
    try:
        return get_karma_from_html(user_id, session=session)
    except requests.RequestException as exc:
        print(f"HTML request failed: {exc}")
        return None

def update_karma_history(karma_value):
    """Update the karma history JSON file with new karma value."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    history_file = data_dir / "karma_history.json"

    # Load existing data or create new
    if history_file.exists():
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = []

    # Add new entry
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if we already have an entry for today
    today_entry = next((item for item in history if item["date"] == today), None)
    if today_entry:
        today_entry["karma"] = karma_value
    else:
        history.append({"date": today, "karma": karma_value})

    # Save updated data
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

def main():
    user_id = os.environ.get("HN_USER_ID", "nkko")  # Default to 'nkko' if env var not set
    print(f"Fetching karma for user: {user_id}")

    karma = get_karma(user_id)
    if karma is not None:
        print(f"Successfully fetched karma: {karma}")
        update_karma_history(karma)
        print("Updated karma history")
    else:
        raise ValueError("Failed to fetch karma points")

if __name__ == "__main__":
    main()
