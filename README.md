# NPS school website

Public site for **Nootan Public School, Dharhara** (नूतन पब्लिक स्कूल, धरहरा). For guardians.

## Live site

https://www.nootanpublicschool.in/

The public HTML is published from this folder (GitHub Pages). Until GoDaddy DNS points `www.nootanpublicschool.in` at GitHub Pages, the site is also available at:

https://amanpandeya5871.github.io/nootan-public-school/

**Deploy:** merge to `main` runs `.github/workflows/pages.yml`. In the repo’s GitHub **Settings → Pages**, set **Source** to **GitHub Actions** (one-time). After DNS is live, set `DEPLOY_CUSTOM_DOMAIN=1` in that workflow before merging so the build writes `CNAME` again.

The working repo stays private; only these files go on the public website.

## Preview

http://localhost:8520/ (or open `index.html`)

**Pages:** Home, About, Facilities, How to reach, Rules, Academics, School life, Admissions, FAQ, Notices, Gallery, Contact.

Crest stays in the header and footer. The home teal band is a Vivekananda quote slider. Section pictures are cartoons. Nav uses dropdowns on About, Academics, and Admissions.

To rebuild every HTML file after editing `_build_pages.py` or `notices/`:

```text
python _build_pages.py
```

## Notices

Festival and jayanti notices are automatic from `notices/events.csv` (dates from the India holiday calendar). Office circulars are drop-in:

```
notices/
  events.csv
  office/ptm/
  office/admit-cards/
  office/results/
  festivals/{slug}/     optional override file
```

See `notices/README.md`. A notice shows 2 days before the date through 1 week after, then on the archive page, then is removed after 6 months.

## Gallery

Drop photos in `gallery/classrooms/` (and the other album folders). Programme albums go in `gallery/events/{name}/` with `title.txt`. See `gallery/README.md`.

## Toppers

Drop a portrait and `card.txt` in `results/toppers/seedling/` (and the other class folders). See `results/toppers/README.md`.

## Brand

- Crest: `assets/npsd-crest.png`
- Teal `#0f766e` · gold `#c9a227` · page `#e8f2ee`
- Type: Playfair Display (name, headings, quotes) · Source Sans 3 (body, nav)
- Office: npsd1970@gmail.com
- Instagram: [nps_dharhara_official](https://www.instagram.com/nps_dharhara_official/)
- Facebook: [Nootan Public School](https://www.facebook.com/profile.php?id=61593511496421)

Gallery frames are empty until the office adds campus photos. Do not add live student photos.

## Out of scope

- Streamlit / staff login on this public site (results stay on the lookup app)
- Online fees
- WhatsApp Cloud API
