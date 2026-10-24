import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "assets" / "contrib-heatmap.svg"
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

def main():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    days = payload["days"]
    if not days:
        raise RuntimeError("Empty contribution dataset.")
    first = date.fromisoformat(days[0]["date"])
    start_ordinal = first.toordinal() - ((first.weekday() + 1) % 7)
    indexed = {(date.fromisoformat(d["date"]).toordinal() - start_ordinal): d for d in days}

    cell, gap, left, top = 12, 4, 34, 43
    shapes, labels, seen = [], [], set()
    for col in range(53):
        for row in range(7):
            item = indexed.get(col * 7 + row)
            if not item:
                continue
            x, y = left + col * (cell + gap), top + row * (cell + gap)
            level = max(0, min(4, int(item["level"])))
            delay = min(col * 0.018 + row * 0.025, 1.5)
            title = escape(f'{item["date"]}: {item["count"]} contributions')
            shapes.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{COLORS[level]}" opacity="0"><title>{title}</title><animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.35s" fill="freeze"/></rect>')
            d = date.fromisoformat(item["date"])
            if d.day <= 7 and (d.year, d.month) not in seen:
                seen.add((d.year, d.month))
                labels.append(f'<text x="{x}" y="27" fill="#8b949e" font-size="10" font-family="monospace">{d.strftime("%b")}</text>')

    total = int(payload.get("total_last_year", sum(d["count"] for d in days)))
    current = int(payload.get("current_streak", 0))
    longest = int(payload.get("longest_streak", 0))
    legend = "".join(f'<rect x="{728+i*16}" y="145" width="11" height="11" rx="2" fill="{c}"/>' for i, c in enumerate(COLORS))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="174" viewBox="0 0 860 174">
<rect width="860" height="174" rx="12" fill="#0d1117" stroke="#30363d"/>
<text x="24" y="22" fill="#39d353" font-size="11" font-family="monospace">CONTRIBUTION ACTIVITY / LAST 365 DAYS</text>
{''.join(labels)}
{''.join(shapes)}
<text x="24" y="157" fill="#c9d1d9" font-size="11" font-family="monospace">{total:,} contributions</text>
<text x="255" y="157" fill="#8b949e" font-size="11" font-family="monospace">current streak: {current}d</text>
<text x="455" y="157" fill="#8b949e" font-size="11" font-family="monospace">longest streak: {longest}d</text>
<text x="686" y="157" fill="#8b949e" font-size="10" font-family="monospace">LESS</text>{legend}
<text x="812" y="157" fill="#8b949e" font-size="10" font-family="monospace">MORE</text>
</svg>'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
