"""Create high-quality web editions of the supplied illustrated guides."""
from pathlib import Path
from shutil import copy2

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "static" / "img" / "guides"
BACKUP = ROOT / "static" / "img" / "guides-original"


def enhance(source: Path, destination: Path) -> None:
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        image = ImageOps.autocontrast(image, cutoff=0.15)
        image = ImageEnhance.Color(image).enhance(1.035)
        image = ImageEnhance.Contrast(image).enhance(1.025)
        image = image.resize((1620, 2025), Image.Resampling.LANCZOS)
        image = image.filter(ImageFilter.UnsharpMask(radius=1.35, percent=115, threshold=3))
        temporary = destination.with_suffix(".enhanced.png")
        image.save(temporary, "PNG", optimize=True, compress_level=7)
        temporary.replace(destination)


BACKUP.mkdir(parents=True, exist_ok=True)
for source_file in sorted(SOURCE.glob("*.png")):
    backup_file = BACKUP / source_file.name
    if not backup_file.exists():
        copy2(source_file, backup_file)
    enhance(source_file, source_file)
