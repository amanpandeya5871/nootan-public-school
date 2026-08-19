"""Resize and write WebP copies of large PNG assets. Run from the repo root."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent / "assets"

RULES = (
    ("npsd-crest.png", 192, 82),
    ("header-leaf.png", 900, 62),
    ("greenery-blur.png", 1200, 62),
    ("cartoon-about.png", 256, 78),
    ("cartoon-academics.png", 256, 78),
    ("cartoon-admissions.png", 256, 78),
    ("cartoon-contact.png", 256, 78),
    ("cartoon-facilities.png", 256, 78),
    ("cartoon-gallery.png", 256, 78),
    ("cartoon-notices.png", 256, 78),
    ("cartoon-school-life.png", 256, 78),
)


def fit(image: Image.Image, max_side: int) -> Image.Image:
    width, height = image.size
    if max(width, height) <= max_side:
        return image
    scale = max_side / max(width, height)
    return image.resize(
        (max(1, int(width * scale)), max(1, int(height * scale))),
        Image.Resampling.LANCZOS,
    )


def to_webp(src: Path, max_side: int, quality: int) -> None:
    image = Image.open(src)
    image = fit(image, max_side)
    dest = src.with_suffix(".webp")
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        image = image.convert("RGBA")
    elif image.mode != "RGB":
        image = image.convert("RGB")
    image.save(dest, "WEBP", quality=quality, method=6)
    print(f"{src.name:28} {src.stat().st_size/1024:7.1f}KB -> {dest.name:28} {dest.stat().st_size/1024:6.1f}KB  {image.size[0]}x{image.size[1]}")


def main() -> None:
    for name, max_side, quality in RULES:
        path = ROOT / name
        if path.exists():
            to_webp(path, max_side, quality)
    for path in sorted((ROOT / "quotes").glob("*.png")):
        to_webp(path, 800, 74)
    toppers = Path(__file__).resolve().parent / "toppers"
    if toppers.is_dir():
        for path in sorted(toppers.glob("*/photo.png")):
            to_webp(path, 700, 74)

    crest = Image.open(ROOT / "npsd-crest.png").convert("RGBA")
    fav = fit(crest, 48)
    fav.save(ROOT / "favicon.png", "PNG", optimize=True)
    apple = fit(crest, 180)
    apple.save(ROOT / "apple-touch.png", "PNG", optimize=True)
    og = fit(crest, 512).convert("RGB")
    og.save(ROOT / "og-crest.jpg", "JPEG", quality=82, optimize=True)
    print(f"favicon.png { (ROOT / 'favicon.png').stat().st_size/1024:.1f}KB")
    print(f"apple-touch.png {(ROOT / 'apple-touch.png').stat().st_size/1024:.1f}KB")
    print(f"og-crest.jpg {(ROOT / 'og-crest.jpg').stat().st_size/1024:.1f}KB")


if __name__ == "__main__":
    main()
