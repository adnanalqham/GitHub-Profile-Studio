import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "adnanalqham")
OUT = Path(__file__).resolve().parents[1] / "data" / "contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"

def main():
    response = requests.get(URL, headers={"User-Agent": "profile-readme-renderer/1.0"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        raise RuntimeError("GitHub contribution cells were not found; markup may have changed. No fake data was generated.")

    days = []
    for cell in cells:
        try:
            day = date.fromisoformat(cell["data-date"])
            raw_count = cell.get("data-count")
            if raw_count is None:
                label = cell.get("aria-label", "")
                tip = cell.find("tool-tip")
                if tip:
                    label = label or tip.get_text(" ", strip=True)
                import re
                match = re.search(r"(\\d[\\d,]*) contribution", label, re.IGNORECASE)
                if match:
                    raw_count = match.group(1).replace(",", "")
                elif "no contributions" in label.lower():
                    raw_count = "0"
                else:
                    raw_count = "0"
            count = int(raw_count)
            level = max(0, min(4, int(cell.get("data-level", "0"))))
            days.append({"date": day.isoformat(), "count": count, "level": level})
        except (KeyError, ValueError, TypeError):
            continue

    cutoff = date.today() - timedelta(days=364)
    days = sorted((d for d in days if date.fromisoformat(d["date"]) >= cutoff), key=lambda d: d["date"])
    if not days:
        raise RuntimeError("No valid contribution dates parsed.")

    counts = {date.fromisoformat(d["date"]): d["count"] for d in days}
    today = date.today()
    cursor = today if counts.get(today, 0) else today - timedelta(days=1)
    current = 0
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    longest = streak = 0
    previous = None
    for item in days:
        d = date.fromisoformat(item["date"])
        if item["count"]:
            streak = streak + 1 if previous and d == previous + timedelta(days=1) else 1
            longest = max(longest, streak)
        else:
            streak = 0
        previous = d

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_last_year": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved {len(days)} days and {payload['total_last_year']} contributions.")

if __name__ == "__main__":
    main()
