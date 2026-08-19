# Notices drop-in

Pages live under this folder: `/notices/board/` and `/notices/archive/`. Individual circulars are `/notices/{slug-date}/`. Do not hand-edit `board/` or `archive/` snapshots — those are filled when the site is rebuilt.

## Yearly festivals and jayantis

Edit `events.csv` to add a row (`observe` = school marks the day on campus, `closed` = holiday). Dates for moving festivals are fetched from the India holiday calendar at build time. Fixed days use `fixed_date` (`MM-DD`).

If a date is missing, add a line to `dates-override.csv`: `year,slug,date`.

To replace the auto sentence with your own circular, drop a `.txt` or image in `festivals/{slug}/`.

## Office circulars

Drop a `.txt` or image in:

- `office/ptm/`
- `office/admit-cards/`
- `office/results/`

Optional `date.txt` with `YYYY-MM-DD`. Otherwise the file date is used.

## Clock

A notice appears on Home and the notice board from 2 days before the date through 1 week after, then only on Notice archive, then is removed after 6 months.

Then run `python _build_pages.py` and push `main`.
