import json
import os
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "adnanalqham")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"


def parse_count(cell):
    # GitHub has used both data-count attributes and accessible tooltip labels.
    raw_count = cell.get("data-count")
    if raw_count is not None:
        return int(raw_count)

    label = cell.get("aria-label", "")
    tooltip = cell.find("tool-tip")
    if tooltip:
        label = f"{label} {tooltip.get_text(' ', strip=True)}".strip()

    match = re.search(r"(\d[\d,]*)\s+contributions?\b", label, re.IGNORECASE)
    if match:
        return int(match.group(1).replace(",", ""))

    if re.search(r"\bno contributions?\b", label, re.IGNORECASE):
        return 0

    # If GitHub changes its markup, don't silently publish an all-zero chart.
    raise ValueError(f"Could not parse contribution count from label: {label!r}")


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
            "GitHub contribution cells were not found; markup may have changed. "
            "No fake data was generated."
        )

    days = []
    for cell in cells:
        try:
            day = date.fromisoformat(cell["data-date"])
            count = parse_count(cell)
            level = max(0, min(4, int(cell.get("data-level", "0"))))
            # Derive the level from the real count if the markup omits it.
            if "data-level" not in cell:
                level = 0 if count == 0 else min(4, 1 + count // 5)
            days.append({"date": day.isoformat(), "count": count, "level": level})
        except (KeyError, ValueError, TypeError) as exc:
            raise RuntimeError(f"Failed to parse a contribution calendar cell: {exc}") from exc

    cutoff = date.today() - timedelta(days=364)
    days = sorted(
        (item for item in days if date.fromisoformat(item["date"]) >= cutoff),
        key=lambda item: item["date"],
    )
    if not days:
        raise RuntimeError("No valid contribution dates parsed.")

    counts = {date.fromisoformat(item["date"]): item["count"] for item in days}
    today = date.today()
    cursor = today if counts.get(today, 0) else today - timedelta(days=1)
    current = 0
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    longest = streak = 0
    previous = None
    for item in days:
        day = date.fromisoformat(item["date"])
        if item["count"]:
            streak = streak + 1 if previous and day == previous + timedelta(days=1) else 1
            longest = max(longest, streak)
        else:
            streak = 0
        previous = day

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_last_year": sum(item["count"] for item in days),
        "current_streak": current,
        "longest_streak": longest,
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"Saved {len(days)} days and {payload['total_last_year']} contributions "
        f"for {USERNAME}."
    )


if __name__ == "__main__":
    main()
