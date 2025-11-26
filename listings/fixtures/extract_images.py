"""
Utility script to extract embedded image_data from the listings fixture
into separate image files, and rewrite the fixture without image_data.

Usage (from project root):

    python -m listings.fixtures.extract_images

This will:
  - Read `listings/fixtures/listings.json`
  - For each `listings.photo` entry with `image_data`:
      * Decode the base64 data
      * Detect the image type (PNG, JPEG, GIF)
      * Write an image file to `listings/fixtures/images/photo_<photo_id>.<ext>`
      * Remove the `image_data` field from the fixture entry
  - Overwrite `listings/fixtures/listings.json` with the updated data
  - Create a backup of the original as `listings/fixtures/listings_with_images.backup.json`

Notes:
  - Image files are NOT meant to be committed to git; they are ignored
    via `.gitignore`. Only the rewritten `listings.json` should be tracked.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import List, Dict, Any


def get_fixtures_dir() -> Path:
    """Return the absolute path to the listings/fixtures directory."""
    return Path(__file__).resolve().parent


def detect_image_extension(image_bytes: bytes) -> str:
    """
    Detect the image file extension based on magic bytes.

    Falls back to 'bin' if the type cannot be determined.
    """
    header = image_bytes[:8]
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if header.startswith(b"\xff\xd8\xff"):
        # Generic JPEG/JFIF header
        return "jpg"
    if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        return "gif"
    return "bin"


def extract_images() -> None:
    fixtures_dir = get_fixtures_dir()
    listings_path = fixtures_dir / "listings.json"
    images_dir = fixtures_dir / "images"

    if not listings_path.exists():
        raise SystemExit(f"Fixture file not found: {listings_path}")

    images_dir.mkdir(parents=True, exist_ok=True)

    # Backup original file before modification
    backup_path = fixtures_dir / "listings_with_images.backup.json"
    if not backup_path.exists():
        backup_path.write_bytes(listings_path.read_bytes())

    data: List[Dict[str, Any]] = json.loads(listings_path.read_text(encoding="utf-8"))

    photos_processed = 0
    photos_with_data = 0

    for obj in data:
        if obj.get("model") != "listings.photo":
            continue

        fields = obj.get("fields") or {}
        image_data_b64 = fields.pop("image_data", None)
        if not image_data_b64:
            continue

        photos_with_data += 1

        try:
            image_bytes = base64.b64decode(image_data_b64)
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Failed to decode image_data for photo pk={obj.get('pk')}: {exc}")
            continue

        ext = detect_image_extension(image_bytes)
        photo_id = obj.get("pk")

        # Use the convention photo_<pk>.<ext> so the management command
        # can find the correct file without needing an extra field
        filename = f"photo_{photo_id}.{ext}"
        image_path = images_dir / filename

        image_path.write_bytes(image_bytes)
        photos_processed += 1

    # Write updated fixture without image_data fields
    listings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"Extraction complete.")
    print(f"  Photos with embedded image_data: {photos_with_data}")
    print(f"  Photos written to files:        {photos_processed}")
    print(f"  Backup of original fixture:     {backup_path}")
    print(f"  Updated fixture (without images): {listings_path}")


if __name__ == "__main__":
    extract_images()


