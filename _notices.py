"""Calendar notices: events.csv, India holiday dates, current/archive windows."""
from __future__ import annotations

import csv
import json
import re
import shutil
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTICES_DIR = ROOT / "notices"
EVENTS_CSV = NOTICES_DIR / "events.csv"
OVERRIDE_CSV = NOTICES_DIR / "dates-override.csv"
DATES_JSON = NOTICES_DIR / "dates.json"
FESTIVALS_DIR = NOTICES_DIR / "festivals"
OFFICE_DIR = NOTICES_DIR / "office"
CURRENT_DIR = NOTICES_DIR / "board"
ARCHIVE_DIR = NOTICES_DIR / "archive"
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

ICS_URL = (
    "https://calendar.google.com/calendar/ical/"
    "en.indian%23holiday%40group.v.calendar.google.com/public/basic.ics"
)
NAGER_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/IN"

CURRENT_BEFORE = 2
CURRENT_AFTER = 7
_CAL_CACHE: list[tuple[date, str]] | None = None
_NOTICE_ITEMS: list[dict] | None = None

OFFICE_SLOTS = (
    {
        "slug": "ptm",
        "title_en": "Parent–teacher meeting",
        "title_hi": "अभिभावक–शिक्षक बैठक",
        "category": "academic",
    },
    {
        "slug": "admit-cards",
        "title_en": "Admit cards",
        "title_hi": "प्रवेश पत्र",
        "category": "academic",
    },
    {
        "slug": "results",
        "title_en": "Results",
        "title_hi": "परिणाम",
        "category": "academic",
    },
)


def add_months(day: date, months: int) -> date:
    month = day.month - 1 + months
    year = day.year + month // 12
    month = month % 12 + 1
    last = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
    return date(year, month, min(day.day, last))


def window_for(event_day: date, today: date) -> str | None:
    start = event_day - timedelta(days=CURRENT_BEFORE)
    current_end = event_day + timedelta(days=CURRENT_AFTER)
    archive_end = add_months(event_day, 6)
    if today < start:
        return None
    if today <= current_end:
        return "current"
    if today <= archive_end:
        return "archive"
    return None


def _http_get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "NPS-Dharhara-site/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def _unfold_ics(text: str) -> list[str]:
    raw = text.replace("\r\n", "\n").split("\n")
    lines: list[str] = []
    for line in raw:
        if line.startswith(" ") or line.startswith("\t"):
            if lines:
                lines[-1] += line[1:]
            continue
        lines.append(line)
    return lines


def parse_ics_events(text: str) -> list[tuple[date, str]]:
    found: list[tuple[date, str]] = []
    summary = ""
    dtstart = ""
    in_event = False
    for line in _unfold_ics(text):
        upper = line.upper()
        if upper == "BEGIN:VEVENT":
            in_event = True
            summary = ""
            dtstart = ""
        elif upper == "END:VEVENT":
            if in_event and summary and dtstart:
                digits = re.sub(r"\D", "", dtstart)[:8]
                if len(digits) == 8:
                    try:
                        found.append((datetime.strptime(digits, "%Y%m%d").date(), summary))
                    except ValueError:
                        pass
            in_event = False
        elif in_event and upper.startswith("SUMMARY"):
            summary = line.split(":", 1)[-1].strip()
        elif in_event and upper.startswith("DTSTART"):
            dtstart = line.split(":", 1)[-1].strip()
    return found


def fetch_calendar_events(years: list[int]) -> list[tuple[date, str]]:
    global _CAL_CACHE
    if _CAL_CACHE is not None:
        return _CAL_CACHE
    events: list[tuple[date, str]] = []
    try:
        ics = _http_get(ICS_URL)
        events.extend(parse_ics_events(ics))
    except Exception as err:
        print(f"notice calendar ICS skipped: {err}")
    if not events:
        for year in years:
            try:
                payload = json.loads(_http_get(NAGER_URL.format(year=year)))
                if isinstance(payload, list):
                    for row in payload:
                        iso = str(row.get("date") or "")
                        name = str(row.get("name") or row.get("localName") or "")
                        if iso and name:
                            events.append((date.fromisoformat(iso), name))
            except Exception as err:
                print(f"notice calendar Nager {year} skipped: {err}")
    _CAL_CACHE = events
    return events


def load_event_rows() -> list[dict[str, str]]:
    if not EVENTS_CSV.exists():
        return []
    with EVENTS_CSV.open(encoding="utf-8", newline="") as handle:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]


def load_overrides() -> dict[tuple[int, str], date]:
    out: dict[tuple[int, str], date] = {}
    if not OVERRIDE_CSV.exists():
        return out
    with OVERRIDE_CSV.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            slug = (row.get("slug") or "").strip()
            try:
                year = int((row.get("year") or "").strip())
                day = date.fromisoformat((row.get("date") or "").strip())
            except ValueError:
                continue
            if slug:
                out[(year, slug)] = day
    return out


def load_dates_cache() -> dict[str, str]:
    if not DATES_JSON.exists():
        return {}
    try:
        data = json.loads(DATES_JSON.read_text(encoding="utf-8"))
        return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def save_dates_cache(mapping: dict[str, str]) -> None:
    DATES_JSON.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _match_title(summary: str, needle: str) -> bool:
    if not needle:
        return False
    return re.search(r"(?i)(?:^|[^A-Za-z])" + re.escape(needle) + r"(?:[^A-Za-z]|$)", summary) is not None


def resolve_date(
    row: dict[str, str],
    year: int,
    cal: list[tuple[date, str]],
    overrides: dict[tuple[int, str], date],
    cache: dict[str, str],
) -> date | None:
    slug = row["slug"]
    key = f"{year}:{slug}"
    if (year, slug) in overrides:
        return overrides[(year, slug)]
    fixed = row.get("fixed_date") or ""
    if re.fullmatch(r"\d{2}-\d{2}", fixed):
        month, day = (int(part) for part in fixed.split("-"))
        try:
            return date(year, month, day)
        except ValueError:
            return None
    needle = row.get("match") or ""
    year_events = [(day, title) for day, title in cal if day.year == year]
    matches = [(day, title) for day, title in year_events if _match_title(title, needle)]
    if matches:
        exact = [day for day, title in matches if title.casefold() == needle.casefold()]
        if exact:
            return exact[0]
        return matches[0][0]
    if year_events:
        return None
    cached = cache.get(key)
    if cached:
        try:
            return date.fromisoformat(cached)
        except ValueError:
            return None
    return None


def first_drop_file(folder: Path) -> Path | None:
    if not folder.is_dir():
        return None
    files = sorted(
        (
            path
            for path in folder.iterdir()
            if path.is_file()
            and not path.name.startswith(".")
            and path.name.lower() not in {"date.txt", "card.txt", "title.txt"}
            and (path.suffix.lower() in IMAGE_EXT or path.suffix.lower() == ".txt")
        ),
        key=lambda path: path.name.lower(),
    )
    return files[0] if files else None


def office_event_date(folder: Path) -> date | None:
    stamp = folder / "date.txt"
    if stamp.exists():
        try:
            return date.fromisoformat(stamp.read_text(encoding="utf-8").strip().split()[0])
        except ValueError:
            pass
    drop = first_drop_file(folder)
    if drop is None:
        return None
    return datetime.fromtimestamp(drop.stat().st_mtime).date()


def festival_override(slug: str) -> Path | None:
    return first_drop_file(FESTIVALS_DIR / slug)


def _wipe_managed(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    keep = folder / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")
    for path in folder.iterdir():
        if path.name in {".gitkeep", "index.html"}:
            continue
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file():
                    child.unlink()
            for child in sorted(path.rglob("*"), reverse=True):
                if child.is_dir():
                    child.rmdir()
            path.rmdir()


def write_snapshot(item: dict, stage: str) -> None:
    dest_root = CURRENT_DIR if stage == "current" else ARCHIVE_DIR
    folder = dest_root / f"{item['date']}-{item['slug']}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "meta.txt").write_text(
        f"{item['title_en']}\n{item['date']}\n{item['kind']}\n",
        encoding="utf-8",
    )


def build_notice_items(today: date | None = None) -> list[dict]:
    global _NOTICE_ITEMS
    if _NOTICE_ITEMS is not None and today is None:
        return _NOTICE_ITEMS
    today = today or date.today()
    years = [today.year - 1, today.year, today.year + 1]
    cal = fetch_calendar_events(years)
    overrides = load_overrides()
    cache = load_dates_cache()
    resolved: dict[str, str] = dict(cache)
    items: list[dict] = []

    for row in load_event_rows():
        slug = row.get("slug") or ""
        if not slug:
            continue
        kind = row.get("kind") or "closed"
        category = "events" if kind == "observe" else "holidays"
        for year in years:
            day = resolve_date(row, year, cal, overrides, cache)
            if day is None:
                continue
            resolved[f"{year}:{slug}"] = day.isoformat()
            stage = window_for(day, today)
            if stage is None:
                continue
            override = festival_override(slug)
            items.append(
                {
                    "slug": slug,
                    "id": f"{slug}-{day.isoformat()}",
                    "date": day.isoformat(),
                    "kind": kind,
                    "source": "calendar",
                    "category": category,
                    "classes": "all",
                    "title_en": row.get("title_en") or slug,
                    "title_hi": row.get("title_hi") or row.get("title_en") or slug,
                    "override": str(override) if override else "",
                    "stage": stage,
                }
            )

    for slot in OFFICE_SLOTS:
        folder = OFFICE_DIR / slot["slug"]
        drop = first_drop_file(folder)
        if drop is None:
            continue
        day = office_event_date(folder)
        if day is None:
            continue
        stage = window_for(day, today)
        if stage is None:
            continue
        items.append(
            {
                "slug": slot["slug"],
                "id": f"{slot['slug']}-{day.isoformat()}",
                "date": day.isoformat(),
                "kind": "office",
                "source": "office",
                "category": slot["category"],
                "classes": "all",
                "title_en": slot["title_en"],
                "title_hi": slot["title_hi"],
                "override": str(drop),
                "stage": stage,
            }
        )

    items.sort(key=lambda item: item["date"], reverse=True)
    _wipe_managed(CURRENT_DIR)
    _wipe_managed(ARCHIVE_DIR)
    for item in items:
        write_snapshot(item, item["stage"])
    legacy_current = NOTICES_DIR / "current"
    if legacy_current.is_dir() and legacy_current.resolve() != CURRENT_DIR.resolve():
        shutil.rmtree(legacy_current)
    save_dates_cache(resolved)
    _NOTICE_ITEMS = items
    return items
