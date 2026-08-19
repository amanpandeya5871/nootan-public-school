"""One-shot HTML builder for the public school site. Run from school-website/."""
from __future__ import annotations

import html
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from _copy import NOTICE_TENSE, QUOTES, academic_year, t
from _notices import build_notice_items
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
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
GALLERY_DIR = ROOT / "gallery"
TOPPERS_DIR = ROOT / "toppers"
TOPPER_CLASSES = (
    ("play", "class_play"),
    ("seedling", "class_seedling"),
    ("sapling", "class_sapling"),
    ("adv", "class_adv"),
    ("class-1", "class_1"),
    ("class-2", "class_2"),
    ("class-3", "class_3"),
    ("class-4", "class_4"),
    ("class-5", "class_5"),
    ("class-6", "class_6"),
    ("class-7", "class_7"),
    ("class-8", "class_8"),
)
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


def load_notices() -> list[dict]:
    return build_notice_items()


def notice_title(site: Site, item: dict) -> str:
    return item["title_hi"] if site.lang == "hi" else item["title_en"]


def notice_tense_lines(site: Site, item: dict) -> dict[str, str] | None:
    kind = item.get("kind") or ""
    if kind not in NOTICE_TENSE:
        return None
    pack = NOTICE_TENSE[kind][site.lang]
    title = notice_title(site, item)
    day = format_date(item["date"])
    return {key: pack[key].format(title=title, date=day) for key in ("before", "on", "after")}


def office_plain_text(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists() or file_path.suffix.lower() in IMAGE_EXT:
        return ""
    return file_path.read_text(encoding="utf-8").strip()


def notice_summary(site: Site, item: dict) -> str:
    lines = notice_tense_lines(site, item)
    if lines:
        return lines["before"]
    override = item.get("override") or ""
    if override:
        text = office_plain_text(override)
        if text:
            return text.split("\n\n")[0].replace("\n", " ")
        return notice_title(site, item)
    return notice_title(site, item)


def notice_cards(site: Site, items: list[dict[str, str]]) -> str:
    bits: list[str] = []
    for item in items:
        href = site.href(f"notice-{item['id']}.html")
        lines = notice_tense_lines(site, item)
        if lines:
            body = (
                f'            <p data-tense="before">{html.escape(lines["before"])}</p>\n'
                f'            <p data-tense="on" hidden>{html.escape(lines["on"])}</p>\n'
                f'            <p data-tense="after" hidden>{html.escape(lines["after"])}</p>'
            )
        else:
            body = f'            <p>{html.escape(notice_summary(site, item))}</p>'
        bits.append(
            f"""          <a class="notice" href="{html.escape(href, quote=True)}" data-event-date="{html.escape(item['date'], quote=True)}" data-notice-kind="{html.escape(item.get('kind') or '', quote=True)}">
            <time datetime="{html.escape(item['date'], quote=True)}">{html.escape(format_date(item['date']))}</time>
            <h3>{html.escape(notice_title(site, item))}</h3>
{body}
          </a>"""
        )
    empty = f'          <p class="prose notice-live-empty" hidden>{site.tx("no_notices")}</p>'
    return ("\n".join(bits) + "\n" + empty) if bits else f'          <p class="prose">{site.tx("no_notices")}</p>'


def notice_category_label(site: Site, category: str) -> str:
    key = f"notices_cat_{category}"
    try:
        return site.tx(key)
    except KeyError:
        return category


def notice_board_html(site: Site, items: list[dict[str, str]], *, filters: bool = False) -> str:
    x = site.tx
    rows: list[str] = []
    for item in items:
        href = site.href(f"notice-{item['id']}.html")
        title = notice_title(site, item)
        lines = notice_tense_lines(site, item)
        summary = lines["before"] if lines else notice_summary(site, item)
        category = item.get("category") or "administrative"
        classes = item.get("classes") or "all"
        cat_label = notice_category_label(site, category)
        search = " ".join((title, summary, cat_label)).lower()
        if lines:
            summary_html = (
                f'<span class="notice-table-summary" data-tense="before">{html.escape(lines["before"])}</span>'
                f'<span class="notice-table-summary" data-tense="on" hidden>{html.escape(lines["on"])}</span>'
                f'<span class="notice-table-summary" data-tense="after" hidden>{html.escape(lines["after"])}</span>'
            )
        else:
            summary_html = f'<span class="notice-table-summary">{html.escape(summary)}</span>'
        rows.append(
            f"""            <tr data-notice data-event-date="{html.escape(item['date'], quote=True)}" data-notice-kind="{html.escape(item.get('kind') or '', quote=True)}" data-category="{html.escape(category, quote=True)}" data-classes="{html.escape(classes, quote=True)}" data-search="{html.escape(search, quote=True)}">
              <td>
                <span class="notice-status">{x("notices_status_active")}</span>
                <time datetime="{html.escape(item["date"], quote=True)}">{html.escape(format_date(item["date"]))}</time>
              </td>
              <td>{html.escape(cat_label)}</td>
              <td>
                <a href="{html.escape(href, quote=True)}">{html.escape(title)}</a>
                {summary_html}
              </td>
              <td><a class="notice-action" href="{html.escape(href, quote=True)}">{x("notices_view")}</a></td>
            </tr>"""
        )
    body = "\n".join(rows) if rows else f'            <tr><td colspan="4">{x("no_notices")}</td></tr>'
    filter_bar = ""
    if filters:
        class_opts = "\n".join(
            f'              <option value="{html.escape(value, quote=True)}">{x(key)}</option>'
            for value, key in (
                ("all", "notices_filter_all"),
                ("play", "form_grade_pre"),
                ("seedling", "form_grade_seedling"),
                ("sapling", "form_grade_sapling"),
                ("adv", "form_grade_adv"),
                ("1-8", "notices_class_18"),
            )
        )
        cat_opts = "\n".join(
            f'              <option value="{html.escape(value, quote=True)}">{x(key)}</option>'
            for value, key in (
                ("all", "notices_filter_all"),
                ("academic", "notices_cat_academic"),
                ("holidays", "notices_cat_holidays"),
                ("events", "notices_cat_events"),
                ("administrative", "notices_cat_administrative"),
            )
        )
        filter_bar = f"""        <form class="notice-filters" data-notice-filters>
          <label>{x("notices_filter_class")}
            <select name="notice-class">
{class_opts}
            </select>
          </label>
          <label>{x("notices_filter_category")}
            <select name="notice-category">
{cat_opts}
            </select>
          </label>
          <label class="notice-filters-search">{x("notices_filter_search")}
            <input name="notice-search" type="search" placeholder="{html.escape(x("notices_filter_search_ph"), quote=True)}" />
          </label>
        </form>
        <p class="notice-filter-empty" hidden>{x("notices_none_filter")}</p>
"""
    return f"""        <div class="notice-board" data-notice-board data-notice-live="{'archive' if filters else 'current'}">
{filter_bar}        <div class="hours-table-wrap">
          <table class="hours-table notice-table">
            <thead>
              <tr>
                <th>{x("notices_col_status")}</th>
                <th>{x("notices_col_category")}</th>
                <th>{x("notices_col_title")}</th>
                <th>{x("notices_col_action")}</th>
              </tr>
            </thead>
            <tbody>
{body}
            </tbody>
          </table>
        </div>
        </div>
"""


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
  <link rel="stylesheet" href="{html.escape(site.asset("css/styles.css"), quote=True)}?v=20260818ap" />
</head>
<body>
  <a class="skip" href="#main">{html.escape(site.tx("skip"))}</a>
  <div class="page-flora" aria-hidden="true">
    <img class="page-flora-leaf" src="{leaf}" alt="" decoding="async" fetchpriority="low" width="900" height="900" />
  </div>
"""


def nav(site: Site, current: str) -> str:
    def cur(name: str) -> str:
        return ' aria-current="page"' if name == current or (name == "notices" and current == "notices-archive") else ""

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
            <li><a href="{h("admissions.html")}#enquiry">{x("nav_enquire")}</a></li>
            <li><a href="{h("faq.html")}"{cur("faq")}>{x("nav_faq")}</a></li>
          </ul>
        </li>
        <li class="has-sub">
          <a href="{h("results.html")}"{cur("results")}>{x("nav_results")}</a>
          <button type="button" class="sub-toggle" aria-expanded="false" aria-label="{html.escape(x("open_sub"), quote=True)}"></button>
          <ul class="sub">
            <li><a href="{h("results.html")}">{x("nav_results_assess")}</a></li>
            <li><a href="{h("results.html")}#lookup">{x("crumb_marksheet")}</a></li>
          </ul>
        </li>
        <li class="has-sub">
          <a href="{h("notices.html")}"{cur("notices")}>{x("nav_notices")}</a>
          <button type="button" class="sub-toggle" aria-expanded="false" aria-label="{html.escape(x("open_sub"), quote=True)}"></button>
          <ul class="sub">
            <li><a href="{h("notices.html")}">{x("nav_notices_board")}</a></li>
            <li><a href="{h("notices-archive.html")}"{cur("notices-archive")}>{x("nav_notices_archive")}</a></li>
          </ul>
        </li>
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
  <script src="{a("js/nav.js")}?v=20260819n"></script>
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


def story(heading: str, body: str, *, section_id: str = "") -> str:
    id_attr = f' id="{html.escape(section_id, quote=True)}"' if section_id else ""
    return f"""    <section class="story"{id_attr}>
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


def album_photos(folder: Path, *, ensure: bool = True) -> list[Path]:
    if ensure:
        folder.mkdir(parents=True, exist_ok=True)
        keep = folder / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
    if not folder.is_dir():
        return []
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


def read_title_file(path: Path) -> tuple[str, str] | None:
    if not path.exists():
        return None
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return None
    english = lines[0]
    hindi = lines[1] if len(lines) > 1 else english
    return english, hindi


def event_albums() -> list[tuple[str, str, str, list[Path]]]:
    root = GALLERY_DIR / "events"
    root.mkdir(parents=True, exist_ok=True)
    keep = root / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")
    found: list[tuple[str, str, str, list[Path]]] = []
    for folder in sorted(root.iterdir(), key=lambda path: path.name.lower(), reverse=True):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        titles = read_title_file(folder / "title.txt")
        photos = album_photos(folder, ensure=False)
        if not titles or not photos:
            continue
        found.append((folder.name, titles[0], titles[1], photos))
    return found


def album_page(slug: str) -> str:
    return f"gallery-{slug}.html"


def event_album_page(slug: str) -> str:
    return f"gallery-event-{slug}.html"


def gallery_slide_visual(site: Site, rel_dir: str, photos: list[Path], *, eager: bool) -> str:
    if not photos:
        return '              <div class="gallery-slide-visual gallery-slide-ph" aria-hidden="true"></div>'
    src = html.escape(site.asset(f"{rel_dir}/{photos[0].name}"), quote=True)
    loading = "" if eager else ' loading="lazy"'
    return (
        f'              <img class="gallery-slide-visual" src="{src}" alt="" '
        f'decoding="async"{loading} />'
    )


def _gallery_slide(site: Site, href: str, label: str, visual: str, *, active: bool) -> str:
    flag = " is-active" if active else ""
    return f"""            <a class="gallery-slide{flag}" href="{html.escape(href, quote=True)}">
{visual}
              <div class="gallery-slide-copy">
                <p class="gallery-slide-kicker">{html.escape(site.tx("nav_gallery"))}</p>
                <h3>{html.escape(label)}</h3>
                <p class="gallery-slide-more">{html.escape(site.tx("gal_view"))}</p>
              </div>
            </a>"""


def gallery_index_html(site: Site) -> str:
    slides: list[str] = []
    jumps: list[str] = []
    index = 0
    for slug, label_key in GALLERY_ALBUMS:
        photos = album_photos(GALLERY_DIR / slug)
        label = site.tx(label_key)
        href = site.href(album_page(slug))
        visual = gallery_slide_visual(site, f"gallery/{slug}", photos, eager=index == 0)
        slides.append(_gallery_slide(site, href, label, visual, active=index == 0))
        jumps.append(f'          <a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>')
        index += 1
    for slug, title_en, title_hi, photos in event_albums():
        label = title_hi if site.lang == "hi" else title_en
        href = site.href(event_album_page(slug))
        visual = gallery_slide_visual(site, f"gallery/events/{slug}", photos, eager=index == 0)
        slides.append(_gallery_slide(site, href, label, visual, active=index == 0))
        jumps.append(f'          <a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>')
        index += 1
    return (
        '        <div class="gallery-carousel" data-gallery-carousel>\n'
        + "\n".join(slides)
        + "\n        </div>\n"
        + f'        <nav class="gallery-jump" aria-label="{html.escape(site.tx("gal_albums"), quote=True)}">\n'
        + "\n".join(jumps)
        + "\n        </nav>\n"
    )


def album_carousel_html(site: Site, rel_dir: str, heading: str, photos: list[Path]) -> str:
    slides: list[str] = []
    for index, path in enumerate(photos):
        active = " is-active" if index == 0 else ""
        src = html.escape(site.asset(f"{rel_dir}/{path.name}"), quote=True)
        loading = "" if index == 0 else ' loading="lazy"'
        alt = html.escape(heading, quote=True)
        slides.append(
            f"""            <figure class="gallery-slide gallery-slide-photo{active}">
              <img class="gallery-slide-visual" src="{src}" alt="{alt}" decoding="async"{loading} />
            </figure>"""
        )
    return (
        '        <div class="gallery-carousel" data-gallery-carousel>\n'
        + "\n".join(slides)
        + "\n        </div>\n"
    )


def _write_album_page(site: Site, filename: str, heading: str, rel_dir: str, photos: list[Path]) -> None:
    if photos:
        body = album_carousel_html(site, rel_dir, heading, photos)
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
        filename,
        f"{heading} · {site.tx('title_gallery')}",
        "gallery",
        main,
        og_meta(site, f"{heading} · NPS Dharhara", site.tx("gal_p")),
    )


def write_gallery_albums(site: Site) -> None:
    folder = ROOT / "hi" if site.lang == "hi" else ROOT
    for old in folder.glob("gallery-*.html"):
        old.unlink()
    for slug, label_key in GALLERY_ALBUMS:
        heading = site.tx(label_key)
        photos = album_photos(GALLERY_DIR / slug)
        _write_album_page(site, album_page(slug), heading, f"gallery/{slug}", photos)
    for slug, title_en, title_hi, photos in event_albums():
        heading = title_hi if site.lang == "hi" else title_en
        _write_album_page(site, event_album_page(slug), heading, f"gallery/events/{slug}", photos)


def write_notice_pages(site: Site, items: list[dict]) -> None:
    folder = ROOT / "hi" if site.lang == "hi" else ROOT
    keep = {f"notice-{item['id']}" for item in items}
    for old in folder.glob("notice-*.html"):
        old.unlink()
    for dest in folder.glob("notice-*"):
        if dest.is_dir() and dest.name not in keep:
            shutil.rmtree(dest)
    for item in items:
        slug = item["id"]
        heading = html.escape(notice_title(site, item))
        date_line = html.escape(format_date(item["date"]))
        override = Path(item["override"]) if item.get("override") else None
        lines = notice_tense_lines(site, item)
        head_date = f'        <p class="notice-date">{date_line} · {html.escape(site.tx("notice_circular"))}</p>\n'
        if override and override.exists() and override.suffix.lower() in IMAGE_EXT:
            rel = override.relative_to(ROOT).as_posix()
            body = (
                head_date
                + f'        <img class="notice-image" src="{html.escape(site.asset(rel), quote=True)}" alt="{heading}" decoding="async" />\n'
            )
        elif override and override.exists() and override.suffix.lower() == ".txt":
            raw = override.read_text(encoding="utf-8").strip()
            paras = "".join(
                f"        <p>{notice_para(chunk.strip(), site.lang)}</p>\n"
                for chunk in raw.split("\n\n")
                if chunk.strip()
            )
            body = head_date + paras
        elif lines:
            body = head_date + (
                f'        <div data-event-date="{html.escape(item["date"], quote=True)}" data-notice-kind="{html.escape(item.get("kind") or "", quote=True)}">\n'
                f'        <p data-tense="before">{html.escape(lines["before"])}</p>\n'
                f'        <p data-tense="on" hidden>{html.escape(lines["on"])}</p>\n'
                f'        <p data-tense="after" hidden>{html.escape(lines["after"])}</p>\n'
                f"        </div>\n"
            )
        else:
            body = f'        <p>{html.escape(site.tx("no_notices"))}</p>\n'
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
            f"{notice_title(site, item)} · {site.tx('brand')}",
            "notices",
            main,
            og_meta(
                site,
                f"{notice_title(site, item)} · NPS Dharhara",
                notice_summary(site, item) or site.tx("og_notice_fallback"),
            ),
        )


def parse_card_txt(path: Path) -> tuple[dict[str, str], dict[str, str]] | None:
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return None
    lines = [line.rstrip() for line in raw.splitlines()]
    name_en = (lines[0] if lines else "").strip()
    name_hi = (lines[1] if len(lines) > 1 else name_en).strip() or name_en
    rest = "\n".join(lines[2:]).strip()
    parts = [chunk.strip() for chunk in rest.split("\n\n") if chunk.strip()]
    quote_en = parts[0] if parts else ""
    quote_hi = parts[1] if len(parts) > 1 else quote_en
    if not name_en or not quote_en:
        return None
    return {"en": name_en, "hi": name_hi}, {"en": quote_en, "hi": quote_hi}


def load_toppers() -> list[dict]:
    items: list[dict] = []
    for slug, class_key in TOPPER_CLASSES:
        folder = TOPPERS_DIR / slug
        photos = album_photos(folder, ensure=True)
        parsed = parse_card_txt(folder / "card.txt")
        if not photos or not parsed:
            continue
        names, quotes = parsed
        rel = photos[0].relative_to(ROOT).as_posix()
        items.append(
            {
                "class_key": class_key,
                "image": rel,
                "name": names,
                "quote": quotes,
            }
        )
    return items
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
          <button type="submit">{x("careers_submit")}</button>
        </form>
        <p class="form-thanks" hidden role="status">{x("careers_thanks")}</p>
        </div>"""


def inquiry_form_html(site: Site) -> str:
    x = site.tx
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
    return f"""        <div class="form-block">
        <form class="form" data-gform="inquiry">
          <input type="hidden" name="language" value="{gform_lang}" />
          <input type="hidden" name="inquiry" value="Admission Process / प्रवेश प्रक्रिया" />
          <p class="form-group-title form-wide">{x("form_student_group")}</p>
          <label class="form-wide">{req_label(site, "form_child")}
            <input name="student" type="text" autocomplete="name" required />
          </label>
          <label>{x("form_age")}
            <input name="age" type="text" />
          </label>
          <label>{req_label(site, "form_grade")}
            <select name="grade" required>
              <option value="">{x("form_choose")}</option>
{grade_options}
            </select>
          </label>
          <p class="form-group-title form-wide">{x("form_parent_group")}</p>
          <label class="form-wide">{req_label(site, "form_guardian")}
            <input name="father" type="text" autocomplete="name" required />
          </label>
          <label>{req_label(site, "form_phone")}
            <input name="phone" type="tel" autocomplete="tel" inputmode="tel" required />
          </label>
          <label>{x("form_email")}
            <input name="email" type="email" autocomplete="email" />
          </label>
          <label class="form-wide">{x("form_address")}
            <input name="address" type="text" autocomplete="street-address" />
          </label>
          <p class="form-group-title form-wide">{x("form_message_group")}</p>
          <label class="form-wide">{x("form_query_enquiry")}
            <textarea name="query"></textarea>
          </label>
          <p class="form-required-key"><span class="form-req">*</span> : {x("form_required_meaning")}</p>
          <button type="submit">{x("form_submit_enquiry")}</button>
        </form>
        <p class="form-thanks" hidden role="status">{x("form_thanks")}</p>
        </div>"""


def build_lang(lang: str) -> None:
    site = Site(lang)
    x = site.tx
    h = site.href
    a = site.asset
    items = load_notices()
    home_cards = notice_cards(site, [item for item in items if item.get("stage") == "current"])

    index_main = f"""  <main id="main">
    <section class="hero hero-welcome">
      <div class="quote-carousel" data-quote-carousel>
          <div class="quote-track">
{quotes_html(site)}
          </div>
        </div>
      <div class="hero-inner wrap">
        <h1>{x("home_hero_title")}</h1>
        <p class="hero-lead">{x("home_hero_sub")}</p>
        <div class="hero-actions">
          <a class="admit-cta" href="{h("admissions.html")}">{x("home_cta_admissions")}</a>
          <a class="admit-cta admit-cta-ghost" href="{h("gallery.html")}">{x("home_cta_campus")}</a>
        </div>
      </div>
    </section>

    <section class="story">
      <h2>{x("home_about")}</h2>
      <div>
        <blockquote class="welcome-quote">
          <p>“{x("home_welcome_quote")}”</p>
        </blockquote>
        <p>{x("home_about_p1")}</p>
        <p>{x("home_about_p2")}</p>
        <a class="learn-more" href="{h("about.html")}">{x("home_about_more")}</a>
      </div>
    </section>

    <section class="cards-block">
      <div class="wrap">
        <p class="section-label">{x("home_pillars_label")}</p>
        <h2 class="section-title">{x("home_pillars_title")}</h2>
        <p class="section-caption">{x("home_pillars_caption")}</p>
        <div class="cards cards-4">
          <article class="card card-plain">
            <h3>{x("home_pillar_1_title")}</h3>
            <p>{x("home_pillar_1_text")}</p>
          </article>
          <article class="card card-plain">
            <h3>{x("home_pillar_2_title")}</h3>
            <p>{x("home_pillar_2_text")}</p>
          </article>
          <article class="card card-plain">
            <h3>{x("home_pillar_3_title")}</h3>
            <p>{x("home_pillar_3_text")}</p>
          </article>
          <article class="card card-plain">
            <h3>{x("home_pillar_4_title")}</h3>
            <p>{x("home_pillar_4_text")}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="cards-block highlights-block">
      <div class="wrap">
        <p class="section-label">{x("home_highlights_label")}</p>
        <h2 class="section-title">{x("home_highlights_title")}</h2>
        <div class="cards">
          <article class="card card-plain">
            <h3>{x("home_highlight_1_title")}</h3>
            <p>{x("home_highlight_1_text")}</p>
          </article>
          <article class="card card-plain">
            <h3>{x("home_highlight_2_title")}</h3>
            <p>{x("home_highlight_2_text")}</p>
          </article>
          <article class="card card-plain">
            <h3>{x("home_highlight_3_title")}</h3>
            <p>{x("home_highlight_3_text")}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="notices" data-notice-live="current">
      <div class="wrap">
        <p class="section-label">{x("home_notices_label")}</p>
        <h2 class="section-title">{x("home_notices_title")}</h2>
        <div class="notice-grid">
{home_cards}
        </div>
        <p class="sample-note">{x("home_notices_note").format(link=notices_link(site, x("home_notices_link")))}</p>
      </div>
    </section>

    <section class="enquire">
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
        + story(x("about_desk"), f"""        <blockquote class="welcome-quote">
          <p>“{x("about_desk_quote")}”</p>
        </blockquote>
""")
        + story(x("about_aim"), f"""        <ul class="plain-list">
          <li><strong>{x("about_vision_label")}:</strong> {x("about_vision")}</li>
          <li><strong>{x("about_mission_label")}:</strong>
            <ul>
              <li>{x("about_mission_1")}</li>
              <li>{x("about_mission_2")}</li>
              <li>{x("about_mission_3")}</li>
            </ul>
          </li>
        </ul>
""")
        + story(x("about_values"), f"""        <ul class="class-list">
          <li><strong>{x("about_value_1_title")}</strong><span>{x("about_value_1_text")}</span></li>
          <li><strong>{x("about_value_2_title")}</strong><span>{x("about_value_2_text")}</span></li>
          <li><strong>{x("about_value_3_title")}</strong><span>{x("about_value_3_text")}</span></li>
          <li><strong>{x("about_value_4_title")}</strong><span>{x("about_value_4_text")}</span></li>
        </ul>
""")
        + story(x("about_web"), f"""        <p>
          <a class="learn-more" href="{h("facilities.html")}">{x("nav_facilities")}</a>
          <a class="learn-more" href="{h("rules.html")}">{x("nav_rules")}</a>
          <a class="learn-more" href="{h("reach.html")}">{x("nav_reach")}</a>
        </p>
""")
    )

    academics_main = (
        banner(x("banner_academics"))
        + crumbs(site, ("academics.html", x("nav_academics")), ("", x("crumb_classes")))
        + story(x("acad_early"), f"""        <p>{x("acad_early_p")}</p>
        <ul class="class-list">
          <li><strong>{x("acad_play_title")}</strong><span>{x("acad_play_text")}</span></li>
          <li><strong>{x("acad_seedling_title")}</strong><span>{x("acad_seedling_text")}</span></li>
          <li><strong>{x("acad_sapling_title")}</strong><span>{x("acad_sapling_text")}</span></li>
          <li><strong>{x("acad_adv_title")}</strong><span>{x("acad_adv_text")}</span></li>
        </ul>
""")
        + story(x("acad_primary"), f"""        <ul class="class-list">
          <li><strong>{x("acad_prim_1_title")}</strong><span>{x("acad_prim_1_text")}</span></li>
          <li><strong>{x("acad_prim_2_title")}</strong><span>{x("acad_prim_2_text")}</span></li>
          <li><strong>{x("acad_prim_3_title")}</strong><span>{x("acad_prim_3_text")}</span></li>
        </ul>
""")
        + story(x("acad_middle"), f"""        <ul class="class-list">
          <li><strong>{x("acad_mid_1_title")}</strong><span>{x("acad_mid_1_text")}</span></li>
          <li><strong>{x("acad_mid_2_title")}</strong><span>{x("acad_mid_2_text")}</span></li>
          <li><strong>{x("acad_mid_3_title")}</strong><span>{x("acad_mid_3_text")}</span></li>
        </ul>
        <p>
          <a class="learn-more" href="{h("school-life.html")}">{x("nav_life")}</a>
          <a class="learn-more" href="{h("admissions.html")}">{x("acad_seat")}</a>
        </p>
""")
    )

    life_main = (
        banner(x("banner_life"))
        + crumbs(site, ("academics.html", x("nav_academics")), ("", x("nav_life")))
        + story(x("life_campus"), f"""        <ul class="class-list">
          <li><strong>{x("life_1_title")}</strong><span>{x("life_1_text")}</span></li>
          <li><strong>{x("life_2_title")}</strong><span>{x("life_2_text")}</span></li>
          <li><strong>{x("life_3_title")}</strong><span>{x("life_3_text")}</span></li>
          <li><strong>{x("life_4_title")}</strong><span>{x("life_4_text")}</span></li>
          <li><strong>{x("life_5_title")}</strong><span>{x("life_5_text")}</span></li>
        </ul>
        <p>
          <a class="learn-more" href="{h("gallery.html")}">{x("nav_gallery")}</a>
          <a class="learn-more" href="{h("facilities.html")}">{x("nav_facilities")}</a>
          <a class="learn-more" href="{h("rules.html")}">{x("nav_rules")}</a>
        </p>
""")
    )

    facilities_main = (
        banner(x("banner_facilities"))
        + crumbs(site, ("about.html", x("nav_about")), ("", x("nav_facilities")))
        + story(x("fac_on"), f"""        <p>{x("fac_on_p1")}</p>
""")
        + story(x("fac_infra"), f"""        <ul class="class-list">
          <li><strong>{x("fac_1_title")}</strong><span>{x("fac_1_text")}</span></li>
          <li><strong>{x("fac_2_title")}</strong><span>{x("fac_2_text")}</span></li>
          <li><strong>{x("fac_3_title")}</strong><span>{x("fac_3_text")}</span></li>
          <li><strong>{x("fac_4_title")}</strong><span>{x("fac_4_text")}</span></li>
          <li><strong>{x("fac_5_title")}</strong><span>{x("fac_5_text")}</span></li>
          <li><strong>{x("fac_6_title")}</strong><span>{x("fac_6_text")}</span></li>
        </ul>
        <p>
          <a class="learn-more" href="{h("contact.html")}">{x("ask_office")}</a>
          <a class="learn-more" href="{h("reach.html")}">{x("nav_reach")}</a>
        </p>
""")
    )

    form_link = f'<a href="#enquiry">{x("adm_form_link")}</a>'
    admissions_main = (
        banner(x("banner_admissions"))
        + crumbs(site, ("admissions.html", x("nav_admissions")), ("", x("adm_overview")))
        + story(x("adm_overview"), f"""        <p>{x("adm_welcome")}</p>
        <p><strong>{x("adm_elig_label")}:</strong> {x("adm_elig")}</p>
        <p><strong>{x("adm_process")}:</strong></p>
        <ol class="plain-list">
          <li>{x("adm_step1").format(form_link=form_link)}</li>
          <li>{x("adm_step2")}</li>
          <li>{x("adm_step3")}</li>
        </ol>
        <p><a class="learn-more" href="{h("faq.html")}">{x("adm_faq")}</a></p>
""")
        + story(
            x("adm_enquire"),
            f"""        <p>{x("adm_enquire_p")}</p>
{inquiry_form_html(site)}
""",
            section_id="enquiry",
        )
    )

    faq_main = (
        banner(x("banner_faq"))
        + crumbs(site, ("admissions.html", x("nav_admissions")), ("", x("nav_faq")))
        + story(
            x("faq_q"),
            f"""        <div class="faq">
          <details name="faq">
            <summary>{x("faq_q1")}</summary>
            <div class="faq-answer">
            {x("faq_a1")}
            </div>
          </details>
          <details name="faq">
            <summary>{x("faq_q2")}</summary>
            <div class="faq-answer">
            {x("faq_a2")}
            </div>
          </details>
          <details name="faq">
            <summary>{x("faq_q3")}</summary>
            <div class="faq-answer">
            {x("faq_a3")}
            </div>
          </details>
          <details name="faq">
            <summary>{x("faq_q4")}</summary>
            <div class="faq-answer">
            {x("faq_a4")}
            </div>
          </details>
          <details name="faq">
            <summary>{x("faq_q5")}</summary>
            <div class="faq-answer">
            {x("faq_a5")}
            </div>
          </details>
        </div>
""",
        )
    )

    notices_main = (
        banner(x("banner_notices"))
        + crumbs(site, ("notices.html", x("nav_notices")), ("", x("nav_notices_board")))
        + story(x("notices_from"), f"""        <p>{x("notices_p")}</p>
""")
        + story(x("notices_latest"), f"""        <ul class="class-list">
          <li><strong>{x("notices_latest_1_title")}</strong><span>{x("notices_latest_1_text")}</span></li>
          <li><strong>{x("notices_latest_2_title")}</strong><span>{x("notices_latest_2_text")}</span></li>
          <li><strong>{x("notices_latest_3_title")}</strong><span>{x("notices_latest_3_text")}</span></li>
          <li><strong>{x("notices_latest_4_title")}</strong><span>{x("notices_latest_4_text")}</span></li>
        </ul>
""")
        + story(
            x("notices_board"),
            f"""{notice_board_html(site, [item for item in items if item.get("stage") == "current"])}
        <p><a class="learn-more" href="{h("notices-archive.html")}">{x("nav_notices_archive")}</a></p>
""",
            section_id="board",
        )
        + story(x("notices_urgent_label"), f"""        <p class="notice-urgent">{x("notices_urgent")}</p>
""")
    )

    notices_archive_main = (
        banner(x("banner_notices"))
        + crumbs(site, ("notices.html", x("nav_notices")), ("", x("nav_notices_archive")))
        + story(
            x("notices_archive"),
            f"""        <p>{x("notices_archive_p")}</p>
{notice_board_html(site, [item for item in items if item.get("stage") == "archive"], filters=True)}
""",
        )
        + story(x("notices_urgent_label"), f"""        <p class="notice-urgent">{x("notices_urgent")}</p>
""")
    )

    gallery_main = (
        banner(x("banner_gallery"))
        + crumbs(site, ("gallery.html", x("nav_gallery")), ("", x("crumb_campus")))
        + story(
            x("gal_h"),
            f"""        <p>{x("gal_p")}</p>
{gallery_index_html(site)}""",
        )
    )

    reach_main = (
        banner(x("banner_reach"))
        + crumbs(site, ("about.html", x("nav_about")), ("", x("nav_reach")))
        + story(x("reach_place"), f"""        <p>{x("reach_p")}</p>
        <dl class="contact-dl">
          <div><dt>{x("reach_name_l")}</dt><dd>{x("reach_name")}</dd></div>
          <div><dt>{x("reach_address_l")}</dt><dd>{x("reach_address")}</dd></div>
          <div><dt>{x("reach_landmark_l")}</dt><dd>{x("reach_landmark")}</dd></div>
        </dl>
{school_map(site)}
""")
        + story(x("reach_visit"), f"""        <ul class="class-list">
          <li><strong>{x("reach_hours_title")}</strong><span>{x("reach_hours_text")}</span></li>
          <li><strong>{x("reach_public_title")}</strong><span>{x("reach_public_text")}</span></li>
          <li><strong>{x("reach_car_title")}</strong><span>{x("reach_car_text")}</span></li>
          <li><strong>{x("reach_tour_title")}</strong><span>{x("reach_tour_text")}</span></li>
        </ul>
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
        <ul class="class-list">
          <li><strong>{x("rules_1_title")}</strong><span>{x("rules_1_text")}</span></li>
          <li><strong>{x("rules_2_title")}</strong><span>{x("rules_2_text")}</span></li>
          <li><strong>{x("rules_3_title")}</strong><span>{x("rules_3_text")}</span></li>
          <li><strong>{x("rules_4_title")}</strong><span>{x("rules_4_text")}</span></li>
          <li><strong>{x("rules_5_title")}</strong><span>{x("rules_5_text")}</span></li>
          <li><strong>{x("rules_6_title")}</strong><span>{x("rules_6_text")}</span></li>
        </ul>
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
        + crumbs(site, ("contact.html", x("nav_contact")), ("", x("contact_touch")))
        + story(x("contact_place"), f"""        <p>{x("contact_intro")}</p>
        <ul class="class-list">
          <li><strong>{x("contact_inst_l")}</strong><span>{x("contact_inst")}</span></li>
          <li><strong>{x("contact_address_l")}</strong><span>{x("contact_address")}</span></li>
          <li><strong>{x("contact_desk_l")}</strong><span>{x("contact_desk")}</span></li>
        </ul>
""")
        + story(x("contact_touch"), f"""        <ul class="class-list">
          <li>
            <strong>{x("contact_email_inq")}</strong>
            <span><a class="contact-link" href="{MAIL}" rel="noopener noreferrer" target="_blank">{ICO_MAIL} npsd1970@gmail.com</a></span>
          </li>
          <li>
            <strong>{x("contact_social_l")}</strong>
            <span>{x("contact_social_p")}</span>
            <span class="contact-social">
              <a class="contact-link" href="{FB}" rel="noopener noreferrer" target="_blank" aria-label="{html.escape(x("footer_fb_aria"), quote=True)}">{ICO_FB} Facebook</a>
              <a class="contact-link" href="{IG}" rel="noopener noreferrer" target="_blank" aria-label="{html.escape(x("footer_ig_aria"), quote=True)}">{ICO_IG} Instagram</a>
            </span>
          </li>
        </ul>
""")
        + story(x("contact_hours"), f"""        <div class="hours-table-wrap">
          <table class="hours-table">
            <thead>
              <tr>
                <th>{x("contact_hours_day")}</th>
                <th>{x("contact_hours_time")}</th>
                <th>{x("contact_hours_svc")}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{x("contact_hours_week")}</td>
                <td>{x("contact_hours_week_t")}</td>
                <td>{x("contact_hours_week_s")}</td>
              </tr>
              <tr>
                <td>{x("contact_hours_sun")}</td>
                <td>{x("contact_hours_closed")}</td>
                <td></td>
              </tr>
            </tbody>
          </table>
        </div>
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

    careers_mail = (
        f'<a class="contact-link" href="{html.escape(mail_href("Application for [Position Name] – [Your Name]"), quote=True)}" '
        f'rel="noopener noreferrer" target="_blank">{ICO_MAIL} npsd1970@gmail.com</a>'
    )
    careers_main = (
        banner(x("banner_careers"))
        + crumbs(site, ("careers.html", x("nav_careers")), ("", x("crumb_apply")))
        + story(x("careers_h"), f"""        <p>{x("careers_intro")}</p>
        <p>{x("careers_intro_2")}</p>
""")
        + story(x("careers_why"), f"""        <ul class="class-list">
          <li><strong>{x("careers_why_1_title")}</strong><span>{x("careers_why_1_text")}</span></li>
          <li><strong>{x("careers_why_2_title")}</strong><span>{x("careers_why_2_text")}</span></li>
          <li><strong>{x("careers_why_3_title")}</strong><span>{x("careers_why_3_text")}</span></li>
          <li><strong>{x("careers_why_4_title")}</strong><span>{x("careers_why_4_text")}</span></li>
        </ul>
""")
        + story(x("careers_open"), f"""        <div class="hours-table-wrap">
          <table class="hours-table">
            <thead>
              <tr>
                <th>{x("careers_col_role")}</th>
                <th>{x("careers_col_level")}</th>
                <th>{x("careers_col_req")}</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>{x("careers_job_1_role")}</td><td>{x("careers_job_1_level")}</td><td>{x("careers_job_1_req")}</td></tr>
              <tr><td>{x("careers_job_2_role")}</td><td>{x("careers_job_2_level")}</td><td>{x("careers_job_2_req")}</td></tr>
              <tr><td>{x("careers_job_3_role")}</td><td>{x("careers_job_3_level")}</td><td>{x("careers_job_3_req")}</td></tr>
              <tr><td>{x("careers_job_4_role")}</td><td>{x("careers_job_4_level")}</td><td>{x("careers_job_4_req")}</td></tr>
              <tr><td>{x("careers_job_5_role")}</td><td>{x("careers_job_5_level")}</td><td>{x("careers_job_5_req")}</td></tr>
            </tbody>
          </table>
        </div>
""")
        + story(x("careers_process"), f"""        <ol class="plain-list">
          <li><strong>{x("careers_step1_title")}:</strong> {x("careers_step1")}</li>
          <li><strong>{x("careers_step2_title")}:</strong> {x("careers_step2")}</li>
          <li><strong>{x("careers_step3_title")}:</strong> {x("careers_step3")}</li>
        </ol>
""")
        + story(
            x("careers_apply"),
            f"""        <p>{x("careers_email_p").format(mail=careers_mail)}</p>
        <p>{x("careers_form_p")}</p>
{hiring_form_html(site)}
        <p>{x("careers_pool")}</p>
""",
            section_id="apply",
        )
    )

    toppers = load_toppers()
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
        for i, item in enumerate(toppers)
    )
    results_main = (
        banner(x("banner_results"))
        + crumbs(site, ("results.html", x("nav_results")), ("", x("nav_results_assess")))
        + story(x("results_eval"), f"""        <p>{x("results_intro")}</p>
        <ul class="class-list">
          <li><strong>{x("results_eval_1_title")}</strong><span>{x("results_eval_1_text")}</span></li>
          <li><strong>{x("results_eval_2_title")}</strong><span>{x("results_eval_2_text")}</span></li>
          <li><strong>{x("results_eval_3_title")}</strong><span>{x("results_eval_3_text")}</span></li>
        </ul>
""", section_id="evaluation")
        + story(x("results_ach"), f"""        <ul class="class-list">
          <li><strong>{x("results_ach_1_title")}</strong><span>{x("results_ach_1_text")}</span></li>
          <li><strong>{x("results_ach_2_title")}</strong><span>{x("results_ach_2_text")}</span></li>
          <li><strong>{x("results_ach_3_title")}</strong><span>{x("results_ach_3_text")}</span></li>
        </ul>
        <p><a class="learn-more" href="#lookup">{x("crumb_marksheet")}</a></p>
""", section_id="achievements")
        + story(
            x("results_see"),
            f"""        <p>{x("results_p1")}</p>
        <p>{x("results_p2")}</p>
        <p>
          <a class="admit-cta" href="{RESULTS_URL}" rel="noopener noreferrer" target="_blank">{x("results_cta")}</a>
        </p>
        <p>{x("results_p3").format(mail=site.mail_link())}</p>
""",
            section_id="lookup",
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
    write_page(site, "notices-archive.html", x("title_notices_archive"), "notices-archive", notices_archive_main, og_meta(site, x("og_notices"), desc))
    write_page(site, "gallery.html", x("title_gallery"), "gallery", gallery_main, og_meta(site, x("og_gallery"), desc))
    write_page(site, "careers.html", x("title_careers"), "careers", careers_main, og_meta(site, x("og_careers"), desc))
    write_page(site, "reach.html", x("title_reach"), "reach", reach_main, og_meta(site, x("og_reach"), desc))
    write_page(site, "rules.html", x("title_rules"), "rules", rules_main, og_meta(site, x("og_rules"), desc))
    write_page(site, "contact.html", x("title_contact"), "contact", contact_main, og_meta(site, x("og_contact"), desc))
    write_notice_pages(site, items)
    write_gallery_albums(site)


def write_publish_files() -> None:
    cname = ROOT / "CNAME"
    cname.write_text(f"{SITE_HOST}\n", encoding="utf-8")
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
  <link rel="stylesheet" href="/css/styles.css?v=20260818ap" />
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
