"""One-shot HTML builder for the public school site. Run from school-website/."""
from __future__ import annotations

import csv
import html
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from _copy import NOTICE_HI, QUOTES, TOPPERS, academic_year, t
from _write_icons import write_icons

ROOT = Path(__file__).resolve().parent
SITE_URL = "https://www.nootanpublicschool.in"
SITE_HOST = "www.nootanpublicschool.in"
FB = "https://www.facebook.com/profile.php?id=61593511496421"
IG = "https://www.instagram.com/nps_dharhara_official/"
MAIL = "https://mail.google.com/mail/?view=cm&fs=1&to=npsd1970@gmail.com"
RESULTS_URL = "https://npsdharhararesults.streamlit.app/"
MAPS_URL = "https://maps.app.goo.gl/nQ6PKQLJfarx8TYy7?g_st=ig"
NOTICES_DIR = ROOT / "notices"
NOTICES_FILES = NOTICES_DIR / "files"
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
GALLERY_DIR = ROOT / "gallery"
GALLERY_ALBUMS = (
    ("classrooms", "gal_1"),
    ("playground", "gal_2"),
    ("assembly", "gal_3"),
    ("campus", "gal_4"),
    ("activities", "gal_5"),
    ("office", "gal_6"),
)
ICO_MAIL = '<svg class="foot-ico" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 6.75A1.75 1.75 0 0 1 4.75 5h14.5A1.75 1.75 0 0 1 21 6.75v10.5A1.75 1.75 0 0 1 19.25 19H4.75A1.75 1.75 0 0 1 3 17.25V6.75Zm1.8.75 7.2 5.1 7.2-5.1H4.8Zm14.45 1.62-6.9 4.88a1.25 1.25 0 0 1-1.5 0L3.95 9.12V17h16.3V9.12Z"/></svg>'
ICO_FB = '<svg class="foot-ico" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h2.6l.4-3H13v-2c0-.6.4-1 1-1Z"/></svg>'
ICO_IG = '<svg class="foot-ico" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 3h8a5 5 0 0 1 5 5v8a5 5 0 0 1-5 5H8a5 5 0 0 1-5-5V8a5 5 0 0 1 5-5Zm0 2a3 3 0 0 0-3 3v8a3 3 0 0 0 3 3h8a3 3 0 0 0 3-3V8a3 3 0 0 0-3-3H8Zm9.2 1.3a1.05 1.05 0 1 1 0 2.1 1.05 1.05 0 0 1 0-2.1ZM12 8.2A3.8 3.8 0 1 1 8.2 12 3.8 3.8 0 0 1 12 8.2Zm0 2A1.8 1.8 0 1 0 13.8 12 1.8 1.8 0 0 0 12 10.2Z"/></svg>'
FONTS = "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&family=Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Serif+Devanagari:wght@600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap"
SITEMAP_URLS: list[str] = []


def pretty_rel(filename: str) -> str:
    if filename in ("", "index.html"):
        return ""
    return f"{Path(filename).stem}/"


def public_path(lang: str, filename: str) -> str:
    rel = pretty_rel(filename)
    if lang == "hi":
        return f"/hi/{rel}" if rel else "/hi/"
    return f"/{rel}" if rel else "/"


def public_url(lang: str, filename: str) -> str:
    return SITE_URL + public_path(lang, filename)


def write_html_redirect(path: Path, dest: str) -> None:
    dest_esc = html.escape(dest, quote=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8" />\n'
        f'  <meta http-equiv="refresh" content="0; url={dest_esc}" />\n'
        f'  <link rel="canonical" href="{html.escape(SITE_URL + dest, quote=True)}" />\n'
        "  <title>Redirecting</title>\n"
        f"  <script>location.replace({json.dumps(dest)});</script>\n"
        "</head>\n"
        f'<body><p><a href="{dest_esc}">Continue</a></p></body>\n'
        "</html>\n",
        encoding="utf-8",
    )


@dataclass
class Site:
    lang: str
    page_file: str = "index.html"

    def tx(self, key: str) -> str:
        return t(self.lang, key)

    def asset(self, path: str) -> str:
        return "/" + path.replace("\\", "/").lstrip("/")

    def href(self, page: str) -> str:
        return public_path(self.lang, page)

    def lang_href(self) -> str:
        other = "en" if self.lang == "hi" else "hi"
        return public_path(other, self.page_file)

    def out_path(self, filename: str) -> Path:
        rel = pretty_rel(filename).strip("/")
        if self.lang == "hi":
            folder = ROOT / "hi" / rel if rel else ROOT / "hi"
        else:
            folder = ROOT / rel if rel else ROOT
        folder.mkdir(parents=True, exist_ok=True)
        return folder / "index.html"

    def mail_link(self, label: str | None = None) -> str:
        text = label or "npsd1970@gmail.com"
        return f'<a href="{MAIL}" rel="noopener noreferrer" target="_blank">{text}</a>'


def mail_href(subject: str = "", body: str = "") -> str:
    url = MAIL
    if subject:
        url += "&su=" + quote(subject)
    if body:
        url += "&body=" + quote(body)
    return url


def page_url(site: Site, filename: str | None = None) -> str:
    return public_url(site.lang, filename or site.page_file)


def og_meta(site: Site, title: str, description: str) -> str:
    desc = html.escape(description, quote=True)
    ttl = html.escape(title, quote=True)
    return (
        f'<meta name="description" content="{desc}" />\n'
        f'  <meta property="og:title" content="{ttl}" />\n'
        f'  <meta property="og:description" content="{desc}" />\n'
        f'  <meta property="og:type" content="website" />'
    )


def format_date(iso: str) -> str:
    try:
        day = datetime.strptime(iso.strip(), "%Y-%m-%d")
        return f"{day.day} {day.strftime('%b %Y')}"
    except ValueError:
        return iso


def slug_from_file(filename: str) -> str:
    return Path(filename).stem


def load_notices() -> list[dict[str, str]]:
    path = NOTICES_DIR / "list.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    items: list[dict[str, str]] = []
    for row in rows:
        file_name = (row.get("file") or "").strip()
        if not file_name:
            continue
        items.append(
            {
                "date": (row.get("date") or "").strip(),
                "title": (row.get("title") or "").strip(),
                "summary": (row.get("summary") or "").strip(),
                "file": file_name,
            }
        )
    items.sort(key=lambda item: item["date"], reverse=True)
    return items


def notice_title(site: Site, item: dict[str, str]) -> str:
    if site.lang == "hi" and item["file"] in NOTICE_HI:
        return NOTICE_HI[item["file"]]["title"]
    return item["title"]


def notice_summary(site: Site, item: dict[str, str]) -> str:
    if site.lang == "hi" and item["file"] in NOTICE_HI:
        return NOTICE_HI[item["file"]]["summary"]
    return item["summary"]


def notice_cards(site: Site, items: list[dict[str, str]]) -> str:
    bits: list[str] = []
    for item in items:
        href = site.href(f"notice-{slug_from_file(item['file'])}.html")
        bits.append(
            f"""          <a class="notice" href="{html.escape(href, quote=True)}">
            <time datetime="{html.escape(item['date'], quote=True)}">{html.escape(format_date(item['date']))}</time>
            <h3>{html.escape(notice_title(site, item))}</h3>
            <p>{html.escape(notice_summary(site, item))}</p>
          </a>"""
        )
    return "\n".join(bits) if bits else f'          <p class="prose">{site.tx("no_notices")}</p>'


def crumbs(site: Site, *parts: tuple[str, str]) -> str:
    bits = [f'<a href="{site.href("index.html")}">{html.escape(site.tx("crumbs_home"))}</a>']
    for href, label in parts[:-1]:
        bits.append(f'<a href="{html.escape(site.href(href), quote=True)}">{html.escape(label)}</a>')
    bits.append(f"<span>{html.escape(parts[-1][1])}</span>")
    inner = '<span class="crumbs-sep" aria-hidden="true">/</span>'.join(bits)
    return f'    <nav class="crumbs wrap" aria-label="Breadcrumb">{inner}</nav>\n'


def quotes_html(site: Site) -> str:
    blocks: list[str] = []
    for index, item in enumerate(QUOTES):
        active = " is-active" if index == 0 else ""
        loading = "" if index == 0 else ' loading="lazy"'
        priority = ' fetchpriority="high"' if index == 0 else ""
        blocks.append(
            f"""            <blockquote class="hero-quote{active}">
              <img class="hero-portrait" src="{html.escape(site.asset(item["image"]), quote=True)}" alt="" decoding="async"{loading}{priority} width="800" height="800" />
              <div class="hero-quote-text">
                <p>“{html.escape(item["text"][site.lang])}”</p>
                <cite>{html.escape(item["cite"][site.lang])}</cite>
              </div>
            </blockquote>"""
        )
    return "\n".join(blocks)


def head(site: Site, title: str, meta: str) -> str:
    canon = html.escape(page_url(site), quote=True)
    en_url = html.escape(public_url("en", site.page_file), quote=True)
    hi_url = html.escape(public_url("hi", site.page_file), quote=True)
    image = html.escape(f"{SITE_URL}/assets/og-crest.jpg", quote=True)
    locale = "hi_IN" if site.lang == "hi" else "en_IN"
    crest = html.escape(site.asset("assets/npsd-crest.webp"), quote=True)
    leaf = html.escape(site.asset("assets/header-leaf.webp"), quote=True)
    favicon = html.escape(site.asset("assets/favicon.png"), quote=True)
    apple = html.escape(site.asset("assets/apple-touch.png"), quote=True)
    preloads = (
        f'  <link rel="preload" as="image" href="{crest}" fetchpriority="high" />\n'
        f'  <link rel="preload" as="image" href="{leaf}" />\n'
    )
    if site.page_file == "index.html":
        first_quote = html.escape(site.asset("assets/quotes/vivekananda.webp"), quote=True)
        preloads += f'  <link rel="preload" as="image" href="{first_quote}" fetchpriority="high" />\n'
    return f"""<!DOCTYPE html>
<html lang="{site.tx("html_lang")}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  {meta}
  <link rel="canonical" href="{canon}" />
  <link rel="alternate" hreflang="en" href="{en_url}" />
  <link rel="alternate" hreflang="hi" href="{hi_url}" />
  <link rel="alternate" hreflang="x-default" href="{en_url}" />
  <meta property="og:url" content="{canon}" />
  <meta property="og:image" content="{image}" />
  <meta property="og:site_name" content="Nootan Public School, Dharhara" />
  <meta property="og:locale" content="{locale}" />
  <link rel="icon" href="{favicon}" sizes="48x48" type="image/png" />
  <link rel="apple-touch-icon" href="{apple}" />
{preloads}  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{FONTS}" rel="stylesheet" />
  <link rel="stylesheet" href="{html.escape(site.asset("css/styles.css"), quote=True)}?v=20260818e" />
</head>
<body>
  <a class="skip" href="#main">{html.escape(site.tx("skip"))}</a>
  <div class="page-flora" aria-hidden="true">
    <img class="page-flora-leaf" src="{leaf}" alt="" decoding="async" fetchpriority="low" width="900" height="900" />
  </div>
"""


def nav(site: Site, current: str) -> str:
    def cur(name: str) -> str:
        return ' aria-current="page"' if name == current else ""

    a = site.asset
    h = site.href
    x = site.tx
    return f"""  <header class="site-header">
    <div class="wrap identity">
      <img class="identity-leaf identity-leaf-left" src="{a("assets/header-leaf.webp")}" alt="" decoding="async" width="900" height="900" />
      <a class="brand" href="{h("index.html")}">
        <img src="{a("assets/npsd-crest.webp")}" width="96" height="96" alt="" decoding="async" fetchpriority="high" />
        <div class="brand-text">
          <p class="brand-name">{html.escape(x("brand"))}</p>
          <p class="brand-place">{html.escape(x("place"))}</p>
        </div>
      </a>
      <img class="identity-leaf identity-leaf-right" src="{a("assets/header-leaf.webp")}" alt="" decoding="async" width="900" height="900" />
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="{html.escape(x("open_menu"), quote=True)}">
        <span></span>
      </button>
    </div>
    <nav class="site-nav" id="site-nav" aria-label="Main">
      <div class="wrap site-nav-bar">
      <ul>
        <li><a href="{h("index.html")}"{cur("home")}>{x("nav_home")}</a></li>
        <li class="has-sub">
          <a href="{h("about.html")}"{cur("about")}>{x("nav_about")}</a>
          <button type="button" class="sub-toggle" aria-expanded="false" aria-label="{html.escape(x("open_sub"), quote=True)}"></button>
          <ul class="sub">
            <li><a href="{h("about.html")}">{x("nav_about_school")}</a></li>
            <li><a href="{h("facilities.html")}"{cur("facilities")}>{x("nav_facilities")}</a></li>
            <li><a href="{h("reach.html")}"{cur("reach")}>{x("nav_reach")}</a></li>
            <li><a href="{h("rules.html")}"{cur("rules")}>{x("nav_rules")}</a></li>
          </ul>
        </li>
        <li class="has-sub">
          <a href="{h("academics.html")}"{cur("academics")}>{x("nav_academics")}</a>
          <button type="button" class="sub-toggle" aria-expanded="false" aria-label="{html.escape(x("open_sub"), quote=True)}"></button>
          <ul class="sub">
            <li><a href="{h("academics.html")}">{x("nav_classes")}</a></li>
            <li><a href="{h("school-life.html")}"{cur("life")}>{x("nav_life")}</a></li>
          </ul>
        </li>
        <li class="has-sub">
          <a href="{h("admissions.html")}"{cur("admissions")}>{x("nav_admissions")}</a>
          <button type="button" class="sub-toggle" aria-expanded="false" aria-label="{html.escape(x("open_sub"), quote=True)}"></button>
          <ul class="sub">
            <li><a href="{h("admissions.html")}">{x("nav_enquire")}</a></li>
            <li><a href="{h("faq.html")}"{cur("faq")}>{x("nav_faq")}</a></li>
          </ul>
        </li>
        <li><a href="{h("results.html")}"{cur("results")}>{x("nav_results")}</a></li>
        <li><a href="{h("notices.html")}"{cur("notices")}>{x("nav_notices")}</a></li>
        <li><a href="{h("gallery.html")}"{cur("gallery")}>{x("nav_gallery")}</a></li>
        <li><a href="{h("careers.html")}"{cur("careers")}>{x("nav_careers")}</a></li>
        <li><a href="{h("contact.html")}"{cur("contact")}>{x("nav_contact")}</a></li>
      </ul>
      <a class="lang-switch" href="{html.escape(site.lang_href(), quote=True)}" hreflang="{"en" if site.lang == "hi" else "hi"}" lang="{"en" if site.lang == "hi" else "hi"}" title="{html.escape(x("lang_title"), quote=True)}">{x("lang_label")}</a>
      </div>
    </nav>
  </header>
"""


def school_map(site: Site) -> str:
    hl = "hi" if site.lang == "hi" else "en"
    embed = (
        "https://maps.google.com/maps?q="
        + quote("Nutan Public School Dharhara Vaishali Bihar 844117")
        + f"&z=16&hl={hl}&output=embed"
    )
    title = html.escape(site.tx("map_title"), quote=True)
    label = html.escape(site.tx("map_open"))
    return f"""        <div class="school-map">
          <a class="map-open" href="{MAPS_URL}" rel="noopener noreferrer" target="_blank">
            {label}
            <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M14 3h7v7h-2V6.4l-9.3 9.3-1.4-1.4L17.6 5H14V3ZM5 5h6v2H7v10h10v-4h2v6H5V5Z"/></svg>
          </a>
          <iframe title="{title}" src="{html.escape(embed, quote=True)}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>
"""


def foot(site: Site) -> str:
    x = site.tx
    h = site.href
    a = site.asset
    return f"""  <footer class="site-footer">
    <div class="wrap footer-grid">
      <div>
        <div class="footer-brand">
          <img src="{a("assets/npsd-crest.webp")}" width="48" height="48" alt="" decoding="async" loading="lazy" />
          <div>
            <strong>{html.escape(x("brand"))}</strong>
            <p class="brand-place">{html.escape(x("place"))}</p>
          </div>
        </div>
{school_map(site)}
      </div>
      <div>
        <h2>{x("footer_quick")}</h2>
        <ul>
          <li><a href="{h("about.html")}">{x("nav_about")}</a></li>
          <li><a href="{h("facilities.html")}">{x("nav_facilities")}</a></li>
          <li><a href="{h("admissions.html")}">{x("nav_admissions")}</a></li>
          <li><a href="{h("results.html")}">{x("nav_results")}</a></li>
          <li><a href="{h("notices.html")}">{x("nav_notices")}</a></li>
          <li><a href="{h("careers.html")}">{x("nav_careers")}</a></li>
          <li><a href="{h("contact.html")}">{x("nav_contact")}</a></li>
        </ul>
      </div>
      <div>
        <h2>{x("footer_school")}</h2>
        <ul>
          <li><a href="{h("academics.html")}">{x("nav_academics")}</a></li>
          <li><a href="{h("school-life.html")}">{x("nav_life")}</a></li>
          <li><a href="{h("rules.html")}">{x("nav_rules")}</a></li>
          <li><a href="{h("gallery.html")}">{x("nav_gallery")}</a></li>
          <li><a href="{h("faq.html")}">{x("nav_faq")}</a></li>
          <li><a href="{h("reach.html")}">{x("nav_reach")}</a></li>
        </ul>
      </div>
      <div>
        <h2>{x("footer_contact")}</h2>
        <ul class="foot-contact">
          <li>
            <a href="{MAIL}" rel="noopener noreferrer" target="_blank">
              {ICO_MAIL}
              npsd1970@gmail.com
            </a>
          </li>
          <li>
            <a href="{FB}" rel="noopener noreferrer" target="_blank" aria-label="{html.escape(x("footer_fb_aria"), quote=True)}">
              {ICO_FB}
              {html.escape(x("footer_fb"))}
            </a>
          </li>
          <li>
            <a href="{IG}" rel="noopener noreferrer" target="_blank" aria-label="{html.escape(x("footer_ig_aria"), quote=True)}">
              {ICO_IG}
              {html.escape(x("footer_ig"))}
            </a>
          </li>
        </ul>
      </div>
    </div>
    <p class="legal">{x("legal")}</p>
  </footer>
  <script src="{a("js/nav.js")}?v=20260818e"></script>
</body>
</html>
"""


def write_page(site: Site, filename: str, title: str, current: str, main: str, meta: str = "") -> None:
    site.page_file = filename
    inner = main if main.strip().startswith("<main") else f'  <main id="main">\n{main}  </main>\n'
    html_out = head(site, title, meta) + nav(site, current) + inner + foot(site)
    site.out_path(filename).write_text(html_out, encoding="utf-8")
    dest = public_path(site.lang, filename)
    SITEMAP_URLS.append(SITE_URL + dest)
    if filename != "index.html":
        stub_dir = ROOT / "hi" if site.lang == "hi" else ROOT
        write_html_redirect(stub_dir / filename, dest)


def banner(heading: str) -> str:
    return f"""    <header class="page-banner">
      <h1>{heading}</h1>
    </header>
"""


def story(heading: str, body: str) -> str:
    return f"""    <section class="story">
      <h2>{heading}</h2>
      <div>
{body.rstrip()}
      </div>
    </section>
"""


def notice_para(text: str, lang: str) -> str:
    year = academic_year(lang)
    escaped = html.escape(text.replace("{year}", year))
    year_esc = html.escape(year)
    return escaped.replace(year_esc, f'<span data-session-year>{year_esc}</span>')


def album_photos(slug: str) -> list[Path]:
    folder = GALLERY_DIR / slug
    folder.mkdir(parents=True, exist_ok=True)
    keep = folder / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")
    return sorted(
        (
            path
            for path in folder.iterdir()
            if path.is_file()
            and path.suffix.lower() in IMAGE_EXT
            and not path.name.startswith(".")
        ),
        key=lambda path: path.name.lower(),
    )


def album_page(slug: str) -> str:
    return f"gallery-{slug}.html"


def gallery_index_tiles(site: Site) -> str:
    tiles = []
    for slug, label_key in GALLERY_ALBUMS:
        photos = album_photos(slug)
        label = html.escape(site.tx(label_key))
        href = html.escape(site.href(album_page(slug)), quote=True)
        if photos:
            src = html.escape(site.asset(f"gallery/{slug}/{photos[0].name}"), quote=True)
            tiles.append(
                f'          <a class="gallery-slot has-photo" href="{href}">'
                f'<img src="{src}" alt="" decoding="async" loading="lazy" /><span>{label}</span></a>'
            )
        else:
            tiles.append(f'          <a class="gallery-slot" href="{href}">{label}</a>')
    return "\n".join(tiles)


def write_gallery_albums(site: Site) -> None:
    folder = ROOT / "hi" if site.lang == "hi" else ROOT
    for old in folder.glob("gallery-*.html"):
        old.unlink()
    for slug, label_key in GALLERY_ALBUMS:
        heading = site.tx(label_key)
        photos = album_photos(slug)
        if photos:
            figures = "\n".join(
                (
                    f'          <a class="gallery-shot" href="{html.escape(site.asset(f"gallery/{slug}/{path.name}"), quote=True)}">'
                    f'<img src="{html.escape(site.asset(f"gallery/{slug}/{path.name}"), quote=True)}" alt="{html.escape(heading, quote=True)}" decoding="async" loading="lazy" /></a>'
                )
                for path in photos
            )
            body = f'        <div class="gallery-album">\n{figures}\n        </div>\n'
        else:
            body = f'        <p class="gallery-empty">{html.escape(site.tx("gal_empty"))}</p>\n'
        main = (
            banner(html.escape(heading))
            + crumbs(site, ("gallery.html", site.tx("nav_gallery")), ("", heading))
            + story(
                html.escape(heading),
                body
                + f'        <p><a class="learn-more" href="{site.href("gallery.html")}">{site.tx("gal_all")}</a></p>\n',
            )
        )
        write_page(
            site,
            album_page(slug),
            f"{heading} · {site.tx('title_gallery')}",
            "gallery",
            main,
            og_meta(site, f"{heading} · NPS Dharhara", site.tx("gal_p")),
        )


def write_notice_pages(site: Site, items: list[dict[str, str]]) -> None:
    folder = ROOT / "hi" if site.lang == "hi" else ROOT
    for old in folder.glob("notice-*.html"):
        old.unlink()
    for item in items:
        src = NOTICES_FILES / item["file"]
        slug = slug_from_file(item["file"])
        ext = Path(item["file"]).suffix.lower()
        heading = html.escape(notice_title(site, item))
        date_line = html.escape(format_date(item["date"]))
        hi_body = NOTICE_HI.get(item["file"], {}).get("body") if site.lang == "hi" else ""
        if not src.exists():
            body = f'        <p>{html.escape(site.tx("no_notices"))}</p>\n'
        elif hi_body:
            paras = "".join(
                f"        <p>{notice_para(chunk.strip(), site.lang)}</p>\n"
                for chunk in hi_body.split("\n\n")
                if chunk.strip()
            )
            body = f'        <p class="notice-date">{date_line} · {html.escape(site.tx("notice_circular"))}</p>\n{paras}'
        elif ext in IMAGE_EXT:
            dest = ROOT / "notices" / "files" / item["file"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            if src.resolve() != dest.resolve():
                shutil.copy2(src, dest)
            body = (
                f'        <p class="notice-date">{date_line} · {html.escape(site.tx("notice_circular"))}</p>\n'
                f'        <img class="notice-image" src="{html.escape(site.asset("notices/files/" + item["file"]), quote=True)}" alt="{heading}" decoding="async" />\n'
            )
        else:
            raw = src.read_text(encoding="utf-8").strip()
            paras = "".join(
                f"        <p>{notice_para(chunk.strip(), site.lang)}</p>\n"
                for chunk in raw.split("\n\n")
                if chunk.strip()
            )
            body = f'        <p class="notice-date">{date_line} · {html.escape(site.tx("notice_circular"))}</p>\n{paras}'
        main = (
            banner(heading)
            + crumbs(site, ("notices.html", site.tx("nav_notices")), ("", notice_title(site, item)))
            + story(
                heading,
                body
                + f'        <p><a class="learn-more" href="{site.href("notices.html")}">{site.tx("all_notices")}</a></p>\n',
            )
        )
        write_page(
            site,
            f"notice-{slug}.html",
            f"{notice_title(site, item)} · {site.tx("brand")}",
            "notices",
            main,
            og_meta(
                site,
                f"{notice_title(site, item)} · NPS Dharhara",
                notice_summary(site, item) or site.tx("og_notice_fallback"),
            ),
        )


def results_link(site: Site) -> str:
    return f'<a href="{site.href("results.html")}">{site.tx("nav_results")}</a>'


def notices_link(site: Site, label: str) -> str:
    return f'<a href="{site.href("notices.html")}">{label}</a>'


def req_mark(site: Site) -> str:
    abbr = html.escape(site.tx("form_required_abbr"), quote=True)
    return f'<abbr class="form-req" title="{abbr}">*</abbr>'


def req_label(site: Site, key: str) -> str:
    text = html.escape(site.tx(key))
    return f'<span class="form-label-text">{text}{req_mark(site)}</span>'


def req_legend(site: Site, key: str) -> str:
    text = html.escape(site.tx(key))
    return f"{text}{req_mark(site)}"


def checkbox_group(name: str, options: list[tuple[str, str]], site: Site) -> str:
    x = site.tx
    return "\n".join(
        f'            <label class="form-choice"><input type="checkbox" name="{name}" value="{html.escape(value, quote=True)}" /> {x(key)}</label>'
        for value, key in options
    )


def hiring_form_html(site: Site) -> str:
    x = site.tx
    gender_radios = "\n".join(
        f'            <label class="form-choice"><input type="radio" name="gender" value="{html.escape(value, quote=True)}" required /> {x(key)}</label>'
        for value, key in (
            ("Male / पुरुष", "form_gender_male"),
            ("Female / महिला", "form_gender_female"),
            ("Other / अन्य", "form_gender_other"),
        )
    )
    qual_options = "\n".join(
        f'              <option value="{html.escape(value, quote=True)}">{x(key)}</option>'
        for value, key in (
            ("Bachelor of Education (B.Ed)", "form_qual_bed"),
            ("Master of Education (M.Ed)", "form_qual_med"),
            ("Post Graduate (PG)", "form_qual_pg"),
            ("Graduate (UG)", "form_qual_ug"),
            ("Other / अन्य", "form_qual_other"),
        )
    )
    subject_checks = checkbox_group(
        "subjects",
        (
            ("Mathematics / गणित", "form_sub_math"),
            ("Science / विज्ञान", "form_sub_sci"),
            ("English / अंग्रेज़ी", "form_sub_eng"),
            ("Hindi / हिंदी", "form_sub_hin"),
            ("Social Studies / सामाजिक अध्ययन", "form_sub_sst"),
            ("Computer / कंप्यूटर", "form_sub_comp"),
            ("Arts & Physical Education / कला और शारीरिक शिक्षा", "form_sub_art"),
            ("EVS / ईवीएस", "form_sub_evs"),
        ),
        site,
    )
    class_checks = checkbox_group(
        "classes",
        (
            ("Pre-Primary (Nursery-KG)", "form_cls_pre"),
            ("Primary (1-5)", "form_cls_pri"),
            ("Middle School (6-8)", "form_cls_mid"),
        ),
        site,
    )
    return f"""        <div class="form-block">
        <form class="form" data-gform="hiring">
          <label class="form-wide">{req_label(site, "careers_name")}
            <input name="name" type="text" autocomplete="name" required />
          </label>
          <label class="form-wide">{req_label(site, "careers_address")}
            <input name="address" type="text" autocomplete="street-address" required />
          </label>
          <label>{x("careers_age")}
            <input name="age" type="text" inputmode="numeric" />
          </label>
          <fieldset class="form-fieldset form-wide">
            <legend>{req_legend(site, "careers_gender")}</legend>
            <div class="form-checks form-checks-inline">
{gender_radios}
            </div>
          </fieldset>
          <label>{req_label(site, "careers_qual")}
            <select name="qualification" required>
              <option value="">{x("form_choose")}</option>
{qual_options}
            </select>
          </label>
          <label>{x("careers_workplace")}
            <input name="workplace" type="text" />
          </label>
          <label>{x("careers_salary")}
            <input name="salary" type="text" inputmode="decimal" />
          </label>
          <fieldset class="form-fieldset form-wide">
            <legend>{x("careers_subjects")}</legend>
            <div class="form-checks">
{subject_checks}
            </div>
          </fieldset>
          <label class="form-wide">{x("careers_subject_other")}
            <input name="subject_other" type="text" />
          </label>
          <fieldset class="form-fieldset form-wide">
            <legend>{x("careers_classes")}</legend>
            <div class="form-checks form-checks-wide">
{class_checks}
            </div>
          </fieldset>
          <label class="form-wide">{x("careers_sample")}
            <input name="sample" type="url" inputmode="url" placeholder="https://" />
          </label>
          <p class="form-required-key"><span class="form-req">*</span> : {x("form_required_meaning")}</p>
          <button type="submit">{x("form_submit")}</button>
        </form>
        <p class="form-thanks" hidden role="status">{x("careers_thanks")}</p>
        </div>"""


def build_lang(lang: str) -> None:
    site = Site(lang)
    x = site.tx
    h = site.href
    a = site.asset
    items = load_notices()
    home_cards = notice_cards(site, items[:3])
    all_cards = notice_cards(site, items)

    index_main = f"""  <main id="main">
    <section class="hero">
      <div class="quote-carousel" data-quote-carousel>
          <div class="quote-track">
{quotes_html(site)}
          </div>
        </div>
    </section>

    <section class="wrap story">
      <h2>{x("home_about")}</h2>
      <div>
        <p>{x("home_about_p1")}</p>
        <p>{x("home_about_p2")}</p>
        <p>{x("home_about_p3")}</p>
        <p>{x("home_about_p4")}</p>
        <a class="learn-more" href="{h("about.html")}">{x("home_about_more")}</a>
      </div>
    </section>

    <section class="cards-block reveal">
      <div class="wrap">
        <p class="section-label">{x("home_explore")}</p>
        <h2 class="section-title">{x("home_start")}</h2>
        <div class="cards">
          <a class="card" href="{h("academics.html")}">
            <div class="card-mark"><img src="{a("assets/cartoon-academics.webp")}" alt="" width="112" height="112" decoding="async" /></div>
            <h3>{x("nav_academics")}</h3>
            <p>{x("card_academics")}</p>
          </a>
          <a class="card" href="{h("results.html")}">
            <div class="card-mark"><img src="{a("assets/cartoon-academics.webp")}" alt="" width="112" height="112" decoding="async" /></div>
            <h3>{x("nav_results")}</h3>
            <p>{x("card_results")}</p>
          </a>
          <a class="card" href="{h("admissions.html")}">
            <div class="card-mark"><img src="{a("assets/cartoon-admissions.webp")}" alt="" width="112" height="112" decoding="async" /></div>
            <h3>{x("nav_admissions")}</h3>
            <p>{x("card_admissions")}</p>
          </a>
          <a class="card" href="{h("contact.html")}">
            <div class="card-mark"><img src="{a("assets/cartoon-contact.webp")}" alt="" width="112" height="112" decoding="async" /></div>
            <h3>{x("nav_contact")}</h3>
            <p>{x("card_contact")}</p>
          </a>
          <a class="card" href="{h("facilities.html")}">
            <div class="card-mark"><img src="{a("assets/cartoon-facilities.webp")}" alt="" width="112" height="112" decoding="async" /></div>
            <h3>{x("nav_facilities")}</h3>
            <p>{x("card_facilities")}</p>
          </a>
          <a class="card" href="{h("school-life.html")}">
            <div class="card-mark"><img src="{a("assets/cartoon-school-life.webp")}" alt="" width="112" height="112" decoding="async" /></div>
            <h3>{x("nav_life")}</h3>
            <p>{x("card_life")}</p>
          </a>
          <a class="card" href="{h("notices.html")}">
            <div class="card-mark"><img src="{a("assets/cartoon-notices.webp")}" alt="" width="112" height="112" decoding="async" /></div>
            <h3>{x("nav_notices")}</h3>
            <p>{x("card_notices")}</p>
          </a>
        </div>
      </div>
    </section>

    <section class="wrap story">
      <h2>{x("home_campus")}</h2>
      <div>
        <p>{x("home_campus_p1")}</p>
        <p>{x("home_campus_p2")}</p>
        <a class="learn-more" href="{h("facilities.html")}">{x("nav_facilities")}</a>
        <a class="learn-more" href="{h("school-life.html")}">{x("nav_life")}</a>
      </div>
    </section>

    <section class="notices reveal">
      <div class="wrap">
        <p class="section-label">{x("home_notices_label")}</p>
        <h2 class="section-title">{x("home_notices_title")}</h2>
        <div class="notice-grid">
{home_cards}
        </div>
        <p class="sample-note">{x("home_notices_note").format(link=notices_link(site, x("home_notices_link")))}</p>
      </div>
    </section>

    <section class="enquire reveal">
      <h2>{x("home_help")}</h2>
      <p>{x("home_help_p")}</p>
      <a class="admit-cta" href="{h("admissions.html")}">{x("home_help_cta")}</a>
      <a class="enquire-mail" href="{MAIL}" rel="noopener noreferrer" target="_blank">{x("home_help_mail")}</a>
    </section>
  </main>
"""

    about_main = (
        banner(x("banner_about"))
        + crumbs(site, ("about.html", x("nav_about")), ("", x("crumb_about_school")))
        + story(x("about_who"), f"""        <p>{x("about_who_p1")}</p>
        <p>{x("about_who_p2")}</p>
""")
        + story(x("about_aim"), f"""        <p>{x("about_aim_p1")}</p>
        <p>{x("about_aim_p2")}</p>
""")
        + story(x("about_web"), f"""        <p>{x("about_web_p1").format(results=results_link(site))}</p>
        <p>
          <a class="learn-more" href="{h("facilities.html")}">{x("nav_facilities")}</a>
          <a class="learn-more" href="{h("rules.html")}">{x("nav_rules")}</a>
          <a class="learn-more" href="{h("reach.html")}">{x("nav_reach")}</a>
        </p>
""")
    )

    academics_main = (
        banner(x("banner_academics"))
        + crumbs(site, ("academics.html", x("nav_academics")), ("", x("crumb_classes")))
        + story(x("acad_path"), f"""        <p>{x("acad_path_p1")}</p>
        <p>{x("acad_path_p2").format(results=results_link(site))}</p>
        <ul class="class-list">
          <li><strong>{x("class_seedling")}</strong><span>{x("subj_early")}</span></li>
          <li><strong>{x("class_sapling")}</strong><span>{x("subj_early")}</span></li>
          <li><strong>{x("class_adv")}</strong><span>{x("subj_adv")}</span></li>
          <li><strong>{x("class_1_5")}</strong><span>{x("subj_15")}</span></li>
          <li><strong>{x("class_6_8")}</strong><span>{x("subj_68")}</span></li>
        </ul>
""")
        + story(x("acad_exams"), f"""        <p>{x("acad_exams_p")}</p>
""")
        + story(x("acad_cal"), f"""        <p>{x("acad_cal_p").format(notices=notices_link(site, x("nav_notices")))}</p>
""")
        + story(x("acad_lang"), f"""        <p>{x("acad_lang_p")}</p>
        <p>
          <a class="learn-more" href="{h("school-life.html")}">{x("nav_life")}</a>
          <a class="learn-more" href="{h("admissions.html")}">{x("acad_seat")}</a>
        </p>
""")
    )

    life_main = (
        banner(x("banner_life"))
        + crumbs(site, ("academics.html", x("nav_academics")), ("", x("nav_life")))
        + story(x("life_day"), f"""        <p>{x("life_day_p1")}</p>
        <p>{x("life_day_p2")}</p>
""")
        + story(x("life_fest"), f"""        <p>{x("life_fest_p")}</p>
""")
        + story(x("life_uniform"), f"""        <p>{x("life_uniform_p")}</p>
""")
        + story(x("life_photo"), f"""        <p>{x("life_photo_p")}</p>
        <p>
          <a class="learn-more" href="{h("gallery.html")}">{x("nav_gallery")}</a>
          <a class="learn-more" href="{h("notices.html")}">{x("nav_notices")}</a>
          <a class="learn-more" href="{h("rules.html")}">{x("nav_rules")}</a>
        </p>
""")
    )

    facilities_main = (
        banner(x("banner_facilities"))
        + crumbs(site, ("about.html", x("nav_about")), ("", x("nav_facilities")))
        + story(x("fac_on"), f"""        <p>{x("fac_on_p1")}</p>
        <p>{x("fac_on_p2")}</p>
""")
        + story(x("fac_more"), f"""        <p>{x("fac_more_p")}</p>
        <p>
          <a class="learn-more" href="{h("contact.html")}">{x("ask_office")}</a>
          <a class="learn-more" href="{h("reach.html")}">{x("nav_reach")}</a>
        </p>
""")
    )

    admissions_main = (
        banner(x("banner_admissions"))
        + crumbs(site, ("admissions.html", x("nav_admissions")), ("", x("crumb_enquire")))
        + story(x("adm_year"), f"""        <p>{x("adm_year_p1")}</p>
        <p>{x("adm_year_p2")}</p>
""")
        + story(x("adm_how"), f"""        <p>{x("adm_how_p").format(mail=site.mail_link())}</p>
""")
        + story(x("adm_papers"), f"""        <p>{x("adm_papers_p")}</p>
""")
        + story(x("life_uniform"), f"""        <p>{x("adm_uniform_p")}</p>
""")
        + story(x("adm_tc"), f"""        <p>{x("adm_tc_p")}</p>
        <p><a class="learn-more" href="{h("faq.html")}">{x("adm_faq")}</a></p>
""")
        + story(x("adm_write"), f"""        <p>{x("adm_write_p")}</p>
        <p>
          <a href="{mail_href(x("mail_subject_adm"))}" rel="noopener noreferrer" target="_blank">npsd1970@gmail.com</a>
        </p>
""")
    )

    faq_main = (
        banner(x("banner_faq"))
        + crumbs(site, ("admissions.html", x("nav_admissions")), ("", x("nav_faq")))
        + story(
            x("faq_q"),
            f"""        <div class="faq">
          <details open>
            <summary>{x("faq_q1")}</summary>
            <p>{x("faq_a1")}</p>
          </details>
          <details>
            <summary>{x("faq_q2")}</summary>
            <p>{x("faq_a2")}</p>
          </details>
          <details>
            <summary>{x("faq_q3")}</summary>
            <p>{x("faq_a3")}</p>
          </details>
          <details>
            <summary>{x("faq_q4")}</summary>
            <p>{x("faq_a4")}</p>
          </details>
          <details>
            <summary>{x("faq_q5")}</summary>
            <p>{x("faq_a5")}</p>
          </details>
          <details>
            <summary>{x("faq_q6")}</summary>
            <p>{x("faq_a6")}</p>
          </details>
          <details>
            <summary>{x("faq_q7")}</summary>
            <p>{x("faq_a7")}</p>
          </details>
        </div>
""",
        )
    )

    notices_main = (
        banner(x("banner_notices"))
        + crumbs(site, ("notices.html", x("nav_notices")), ("", x("crumb_from_office")))
        + story(
            x("notices_from"),
            f"""        <p>{x("notices_p")}</p>
        <div class="notice-grid">
{all_cards}
        </div>
""",
        )
    )

    gallery_main = (
        banner(x("banner_gallery"))
        + crumbs(site, ("gallery.html", x("nav_gallery")), ("", x("crumb_campus")))
        + story(
            x("gal_h"),
            f"""        <p>{x("gal_p")}</p>
        <div class="gallery-grid">
{gallery_index_tiles(site)}
        </div>
""",
        )
    )

    reach_main = (
        banner(x("banner_reach"))
        + crumbs(site, ("about.html", x("nav_about")), ("", x("nav_reach")))
        + story(x("reach_place"), f"""        <p>{x("reach_p")}</p>
{school_map(site)}
""")
        + story(
            x("reach_follow"),
            f"""        <ul class="contact-links">
          <li><a href="{MAIL}" rel="noopener noreferrer" target="_blank">{ICO_MAIL} npsd1970@gmail.com</a></li>
          <li><a href="{FB}" rel="noopener noreferrer" target="_blank" aria-label="{html.escape(x("footer_fb_aria"), quote=True)}">{ICO_FB} {html.escape(x("footer_fb"))}</a></li>
          <li><a href="{IG}" rel="noopener noreferrer" target="_blank" aria-label="{html.escape(x("footer_ig_aria"), quote=True)}">{ICO_IG} {html.escape(x("footer_ig"))}</a></li>
        </ul>
""",
        )
    )

    rules_main = (
        banner(x("banner_rules"))
        + crumbs(site, ("about.html", x("nav_about")), ("", x("nav_rules")))
        + story(x("rules_in"), f"""        <p>{x("rules_in_p")}</p>
""")
        + story(x("rules_circ"), f"""        <p>{x("rules_circ_p")}</p>
""")
        + story(x("rules_visit"), f"""        <p>{x("rules_visit_p")}</p>
""")
        + story(x("rules_priv"), f"""        <p>{x("rules_priv_p")}</p>
        <p>
          <a class="learn-more" href="{h("notices.html")}">{x("nav_notices")}</a>
          <a class="learn-more" href="{h("contact.html")}">{x("nav_contact")}</a>
        </p>
""")
    )

    gform_lang = "Hindi" if site.lang == "hi" else "English"
    grade_options = "\n".join(
        f'              <option value="{html.escape(value, quote=True)}">{x(key)}</option>'
        for value, key in (
            ("Pre-Nursery", "form_grade_pre"),
            ("Seedling (Nursery)", "form_grade_seedling"),
            ("Sapling (LKG)", "form_grade_sapling"),
            ("Advance Sapling (UKG)", "form_grade_adv"),
            ("Class 1", "form_grade_1"),
            ("Class 2", "form_grade_2"),
            ("Class 3", "form_grade_3"),
            ("Class 4", "form_grade_4"),
            ("Class 5", "form_grade_5"),
            ("Class 6", "form_grade_6"),
            ("Class 7", "form_grade_7"),
            ("Class 8", "form_grade_8"),
        )
    )
    inquiry_options = "\n".join(
        f'              <option value="{html.escape(value, quote=True)}">{x(key)}</option>'
        for value, key in (
            ("Admission Process / प्रवेश प्रक्रिया", "form_inq_adm"),
            ("Fee Structure / शुल्क विवरण", "form_inq_fee"),
            ("Exam Schedule / परीक्षा कार्यक्रम", "form_inq_exam"),
            ("Other / अन्य", "form_inq_other"),
        )
    )
    contact_main = (
        banner(x("banner_contact"))
        + crumbs(site, ("contact.html", x("nav_contact")), ("", x("crumb_write")))
        + story(
            x("contact_school"),
            f"""        <dl class="contact-dl">
          <div>
            <dt>{x("contact_school")}</dt>
            <dd>{x("contact_school_name")}</dd>
          </div>
          <div>
            <dt>{x("contact_place_l")}</dt>
            <dd class="brand-place">{html.escape(x("place"))}</dd>
          </div>
          <div>
            <dt>{x("contact_email_l")}</dt>
            <dd><a class="contact-link" href="{MAIL}" rel="noopener noreferrer" target="_blank">{ICO_MAIL} npsd1970@gmail.com</a></dd>
          </div>
          <div>
            <dt>Facebook</dt>
            <dd><a class="contact-link" href="{FB}" rel="noopener noreferrer" target="_blank">{ICO_FB} {html.escape(x("fb_name"))}</a></dd>
          </div>
          <div>
            <dt>Instagram</dt>
            <dd><a class="contact-link" href="{IG}" rel="noopener noreferrer" target="_blank">{ICO_IG} nps_dharhara_official</a></dd>
          </div>
        </dl>
""",
        )
        + story(x("contact_circ"), f"""        <p>{x("contact_circ_p")}</p>
""")
        + story(
            x("contact_write"),
            f"""        <p>{x("contact_write_p")}</p>
        <div class="form-block">
        <form class="form" data-gform="inquiry">
          <input type="hidden" name="language" value="{gform_lang}" />
          <label class="form-wide">{req_label(site, "form_student")}
            <input name="student" type="text" autocomplete="name" required />
          </label>
          <label>{req_label(site, "form_father")}
            <input name="father" type="text" autocomplete="name" required />
          </label>
          <label>{req_label(site, "form_mother")}
            <input name="mother" type="text" autocomplete="name" required />
          </label>
          <label>{req_label(site, "form_phone")}
            <input name="phone" type="tel" autocomplete="tel" inputmode="tel" required />
          </label>
          <label>{x("form_email")}
            <input name="email" type="email" autocomplete="email" />
          </label>
          <label>{x("form_grade")}
            <select name="grade">
              <option value="">{x("form_choose")}</option>
{grade_options}
            </select>
          </label>
          <label>{x("form_inquiry")}
            <select name="inquiry">
              <option value="">{x("form_choose")}</option>
{inquiry_options}
            </select>
          </label>
          <label class="form-wide">{x("form_query")}
            <textarea name="query"></textarea>
          </label>
          <p class="form-required-key"><span class="form-req">*</span> : {x("form_required_meaning")}</p>
          <button type="submit">{x("form_submit")}</button>
        </form>
        <p class="form-thanks" hidden role="status">{x("form_thanks")}</p>
        </div>
""",
        )
    )

    careers_main = (
        banner(x("banner_careers"))
        + crumbs(site, ("careers.html", x("nav_careers")), ("", x("crumb_apply")))
        + story(
            x("careers_apply"),
            f"""        <p>{x("careers_intro")}</p>
{hiring_form_html(site)}
""",
        )
    )

    topper_cards = "\n".join(
        f"""          <article class="topper-card{' is-active' if i == 0 else ''}">
            <div class="topper-photo">
              <img src="{html.escape(site.asset(item["image"]), quote=True)}" alt="" decoding="async"{' fetchpriority="high"' if i == 0 else ' loading="lazy"'} width="466" height="700" />
            </div>
            <div class="topper-copy">
              <h3>{x(item["class_key"])}</h3>
              <p class="topper-quote-label">{x("topper_said")}</p>
              <p class="topper-quote">“{html.escape(item["quote"][site.lang])}”</p>
              <p class="topper-name">— {html.escape(item["name"][site.lang])}</p>
            </div>
          </article>"""
        for i, item in enumerate(TOPPERS)
    )
    results_main = (
        banner(x("banner_results"))
        + crumbs(site, ("results.html", x("nav_results")), ("", x("crumb_marksheet")))
        + story(
            x("results_see"),
            f"""        <p>{x("results_p1")}</p>
        <p>{x("results_p2")}</p>
        <p>
          <a class="admit-cta" href="{RESULTS_URL}" rel="noopener noreferrer" target="_blank">{x("results_cta")}</a>
        </p>
        <p>{x("results_p3").format(mail=site.mail_link())}</p>
""",
        )
        + story(
            x("toppers"),
            f"""        <p>{x("toppers_p")}</p>
        <div class="toppers-carousel" data-topper-carousel>
{topper_cards}
        </div>
""",
        )
    )

    desc = x("site_desc")
    write_page(site, "index.html", x("title_home"), "home", index_main, og_meta(site, x("title_home"), desc))
    write_page(site, "about.html", x("title_about"), "about", about_main, og_meta(site, x("og_about"), desc))
    write_page(site, "academics.html", x("title_academics"), "academics", academics_main, og_meta(site, x("og_academics"), desc))
    write_page(site, "school-life.html", x("title_life"), "life", life_main, og_meta(site, x("og_life"), desc))
    write_page(site, "facilities.html", x("title_facilities"), "facilities", facilities_main, og_meta(site, x("og_facilities"), desc))
    write_page(site, "admissions.html", x("title_admissions"), "admissions", admissions_main, og_meta(site, x("og_admissions"), desc))
    write_page(site, "results.html", x("title_results"), "results", results_main, og_meta(site, x("og_results"), x("results_desc")))
    write_page(site, "faq.html", x("title_faq"), "faq", faq_main, og_meta(site, x("og_faq"), desc))
    write_page(site, "notices.html", x("title_notices"), "notices", notices_main, og_meta(site, x("og_notices"), desc))
    write_page(site, "gallery.html", x("title_gallery"), "gallery", gallery_main, og_meta(site, x("og_gallery"), desc))
    write_page(site, "careers.html", x("title_careers"), "careers", careers_main, og_meta(site, x("og_careers"), desc))
    write_page(site, "reach.html", x("title_reach"), "reach", reach_main, og_meta(site, x("og_reach"), desc))
    write_page(site, "rules.html", x("title_rules"), "rules", rules_main, og_meta(site, x("og_rules"), desc))
    write_page(site, "contact.html", x("title_contact"), "contact", contact_main, og_meta(site, x("og_contact"), desc))
    write_notice_pages(site, items)
    write_gallery_albums(site)


def write_publish_files() -> None:
    cname = ROOT / "CNAME"
    if os.environ.get("DEPLOY_CUSTOM_DOMAIN") == "1":
        cname.write_text(f"{SITE_HOST}\n", encoding="utf-8")
    elif cname.exists():
        cname.unlink()
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )
    urls = [f"  <url><loc>{html.escape(loc)}</loc></url>" for loc in dict.fromkeys(SITEMAP_URLS)]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n",
        encoding="utf-8",
    )
    (ROOT / "404.html").write_text(
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Page not found · Nootan Public School, Dharhara</title>
  <meta http-equiv="refresh" content="4; url=/" />
  <link rel="stylesheet" href="/css/styles.css?v=20260818e" />
</head>
<body>
  <main id="main" class="wrap" style="padding: 4rem 1rem 6rem">
    <h1>This page is not on the school website.</h1>
    <p><a class="learn-more" href="/">Return to the home page</a></p>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def build() -> None:
    SITEMAP_URLS.clear()
    write_icons()
    build_lang("en")
    build_lang("hi")
    write_publish_files()
    print("wrote pages (en + hi)")


if __name__ == "__main__":
    build()
