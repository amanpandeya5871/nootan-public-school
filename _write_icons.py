"""Circular name-seals (gold/teal, like the school crest, unique inner mark)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "icons"

# Inner marks sit in the cream disc (viewBox 200).
MARKS = {
    "academics": """
      <path d="M55 108 L100 92 L145 108 L100 124 Z" fill="none" stroke="#0f766e" stroke-width="4" stroke-linejoin="round"/>
      <path d="M100 92 V124" stroke="#c9a227" stroke-width="3"/>
      <path d="M70 108 Q100 118 130 108" fill="none" stroke="#b91c1c" stroke-width="2"/>
    """,
    "admissions": """
      <rect x="78" y="78" width="44" height="52" rx="2" fill="none" stroke="#0f766e" stroke-width="4"/>
      <path d="M78 78 L100 62 L122 78" fill="none" stroke="#c9a227" stroke-width="4" stroke-linejoin="round"/>
      <circle cx="112" cy="108" r="3" fill="#c9a227"/>
    """,
    "contact": """
      <rect x="62" y="88" width="76" height="48" rx="3" fill="none" stroke="#0f766e" stroke-width="4"/>
      <path d="M62 92 L100 114 L138 92" fill="none" stroke="#c9a227" stroke-width="3" stroke-linejoin="round"/>
    """,
    "facilities": """
      <rect x="70" y="96" width="60" height="36" fill="none" stroke="#0f766e" stroke-width="4"/>
      <path d="M64 96 H136 L100 70 Z" fill="none" stroke="#c9a227" stroke-width="4" stroke-linejoin="round"/>
      <rect x="92" y="108" width="16" height="24" fill="#0f766e"/>
    """,
    "school-life": """
      <circle cx="100" cy="86" r="10" fill="none" stroke="#c9a227" stroke-width="3"/>
      <path d="M78 130 Q100 108 122 130" fill="none" stroke="#0f766e" stroke-width="4"/>
      <path d="M70 92 L80 100 M130 92 L120 100 M100 70 V78" stroke="#c9a227" stroke-width="3" stroke-linecap="round"/>
    """,
    "notices": """
      <rect x="72" y="76" width="56" height="64" rx="2" fill="none" stroke="#0f766e" stroke-width="4"/>
      <line x1="84" y1="96" x2="116" y2="96" stroke="#c9a227" stroke-width="3"/>
      <line x1="84" y1="108" x2="116" y2="108" stroke="#c9a227" stroke-width="3"/>
      <line x1="84" y1="120" x2="108" y2="120" stroke="#c9a227" stroke-width="3"/>
    """,
    "gallery": """
      <rect x="68" y="82" width="64" height="50" fill="none" stroke="#c9a227" stroke-width="5"/>
      <rect x="76" y="90" width="48" height="34" fill="none" stroke="#0f766e" stroke-width="3"/>
      <path d="M80 118 L92 104 L104 114 L112 106 L120 118 Z" fill="#0f766e"/>
    """,
    "about": """
      <rect x="74" y="94" width="52" height="38" fill="none" stroke="#0f766e" stroke-width="4"/>
      <path d="M68 94 H132 L100 70 Z" fill="none" stroke="#c9a227" stroke-width="4" stroke-linejoin="round"/>
      <rect x="94" y="110" width="12" height="22" fill="#0f766e"/>
    """,
    "faq": """
      <circle cx="100" cy="100" r="28" fill="none" stroke="#0f766e" stroke-width="4"/>
      <text x="100" y="112" text-anchor="middle" font-size="36" font-family="Georgia, serif" font-weight="700" fill="#c9a227">?</text>
    """,
    "reach": """
      <path d="M100 72 C86 72 76 84 76 96 C76 114 100 132 100 132 C100 132 124 114 124 96 C124 84 114 72 100 72 Z" fill="none" stroke="#0f766e" stroke-width="4"/>
      <circle cx="100" cy="96" r="8" fill="#c9a227"/>
    """,
}

LABELS = {
    "academics": ("ACADEMICS", "NPS"),
    "admissions": ("ADMISSIONS", "NPS"),
    "contact": ("CONTACT", "NPS"),
    "facilities": ("FACILITIES", "NPS"),
    "school-life": ("SCHOOL LIFE", "NPS"),
    "notices": ("NOTICES", "NPS"),
    "gallery": ("GALLERY", "NPS"),
    "about": ("ABOUT", "NPS"),
    "faq": ("FAQ", "NPS"),
    "reach": ("HOW TO REACH", "NPS"),
}


def _svg(slug: str) -> str:
    top, bot = LABELS[slug]
    size = 11 if len(top) > 10 else 13
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" role="img" aria-label="{top}">
  <circle cx="100" cy="100" r="99" fill="#c9a227"/>
  <circle cx="100" cy="100" r="93" fill="#0a3d2c"/>
  <circle cx="100" cy="100" r="68" fill="#c9a227"/>
  <circle cx="100" cy="100" r="63" fill="#f7faf8"/>
  <defs>
    <path id="arc-top-{slug}" d="M 38 100 A 62 62 0 0 1 162 100"/>
    <path id="arc-bot-{slug}" d="M 162 100 A 62 62 0 0 1 38 100"/>
  </defs>
  <text fill="#ffffff" font-size="{size}" font-family="IBM Plex Sans, Segoe UI, sans-serif" font-weight="700" letter-spacing="2">
    <textPath href="#arc-top-{slug}" startOffset="50%" text-anchor="middle">{top}</textPath>
  </text>
  <text fill="#ffffff" font-size="12" font-family="IBM Plex Sans, Segoe UI, sans-serif" font-weight="700" letter-spacing="4">
    <textPath href="#arc-bot-{slug}" startOffset="50%" text-anchor="middle">{bot}</textPath>
  </text>
  {MARKS[slug]}
</svg>
"""


def write_icons() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug in LABELS:
        (OUT / f"{slug}.svg").write_text(_svg(slug), encoding="utf-8")


if __name__ == "__main__":
    write_icons()
    print("wrote", len(LABELS), "icons")
