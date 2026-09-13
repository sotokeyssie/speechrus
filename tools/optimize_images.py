"""Build lightweight WebP variants while retaining original source artwork."""
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "static" / "img"
targets = [
    *IMAGE_ROOT.glob("characters-*.png"),
    *(IMAGE_ROOT / "articles").glob("*.png"),
    *(IMAGE_ROOT / "guides").glob("*.png"),
    IMAGE_ROOT / "brand" / "centro-terapias-hero.png",
    IMAGE_ROOT / "brand" / "flyer-integradas.png",
]

for source in targets:
    if not source.is_file():
        continue
    destination = source.with_suffix(".webp")
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        quality = 94 if source.parent.name == "guides" else 90
        image.save(destination, "WEBP", quality=quality, method=6)
