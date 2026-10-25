import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "adnanalqham")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"


def main():
    response = requests.get(
        URL,
        headers={"User-Agent": "profile-readme-renderer/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select(".ContributionCalendar-day[data-date]")
    if not cells:
        raise RuntimeError(
            "GitHub contribution cells were not found; markup may have changed."
        )

    days = []
    for cell in cells:
        try:
            day = date.fromisoformat(cell["data-date"])
            level = max(0, min(4, int(cell.get("data-level", "0"))))
            # The current public HTML exposes activity levels but not reliable
            # numeric counts. Keep counts unknown rather than inventing them.
            days.append({
                "date": day.isoformat(),
                "count": None,
                "level": level,
                "active": level > 0,
            })
        except (KeyError, ValueError, TypeError) as exc:
            raise RuntimeError(f"Failed to parse a contribution calendar cell: {exc}") from exc

    cutoff = date.today() - timedelta(days=364)
    days = sorted(
        (item for item in days if date.fromisoformat(item["date"]) >= cutoff),
        key=lambda item: item["date"],
    )
    if not days:
        raise RuntimeError("No valid contribution dates parsed.")

    active_by_date = {
        date.fromisoformat(item["date"]): item["active"] for item in days
    }
    today = date.today()
    cursor = today if active_by_date.get(today, False) else today - timedelta(days=1)
    current = 0
    while active_by_date.get(cursor, False):
        current += 1
        cursor -= timedelta(days=1)

    longest = streak = 0
    previous = None
    for item in days:
        day = date.fromisoformat(item["date"])
        if item["active"]:
            streak = streak + 1 if previous and day == previous + timedelta(days=1) else 1
            longest = max(longest, streak)
        else:
            streak = 0
        previous = day

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_last_year": None,
        "active_days_last_year": sum(1 for item in days if item["active"]),
        "current_streak": current,
        "longest_streak": longest,
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"Saved {len(days)} activity levels for {USERNAME}; "
        f"{payload['active_days_last_year']} active days. Exact counts are not "
        "exposed in the public HTML, so none were fabricated."
    )


if __name__ == "__main__":
    main()
