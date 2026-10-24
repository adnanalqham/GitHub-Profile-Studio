from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "info-card.svg"

PROFILE = {
    "USER": "adnanalqham",
    "ROLE": "Software Developer / Digital Marketing Specialist",
    "BASE": "Sana'a, Yemen",
    "FOCUS": "Web apps · Mobile apps · Automation",
    "STACK": "Flutter · Expo / React Native · TypeScript · NestJS",
    "DATA": "PostgreSQL · Prisma · SQLite",
    "BUILDS": "Aoun · Hotel systems · YouTube Downloader",
    "NOW": "Building practical products and workflows",
}

def main():
    rows = []
    for i, (key, value) in enumerate(PROFILE.items()):
        y = 59 + i * 27
        delay = i * 0.12
        rows.append(f'''<g opacity="0">
<text x="38" y="{y}" fill="#39d353" font-size="13" font-family="monospace">{escape(key)}</text>
<text x="174" y="{y}" fill="#c9d1d9" font-size="13" font-family="monospace">{escape(value)}</text>
<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.3s" fill="freeze"/>
</g>''')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="294" viewBox="0 0 860 294">
<rect width="860" height="294" rx="12" fill="#0d1117" stroke="#30363d"/>
<path d="M12 0 H848 Q860 0 860 12 V38 H0 V12 Q0 0 12 0Z" fill="#161b22"/>
<circle cx="20" cy="19" r="5" fill="#ff5f56"/><circle cx="38" cy="19" r="5" fill="#ffbd2e"/><circle cx="56" cy="19" r="5" fill="#27c93f"/>
<text x="78" y="23" fill="#8b949e" font-size="11" font-family="monospace">adnanalqham — developer profile</text>
<text x="24" y="46" fill="#8b949e" font-size="10" font-family="monospace">$ neofetch --profile</text>
{''.join(rows)}
</svg>'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
