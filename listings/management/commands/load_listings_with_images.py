"""
Custom management command to load listings fixtures and attach image data
from files extracted by `listings/fixtures/extract_images.py`.

Typical workflow:

1. (One-time) Extract embedded images from the large fixture:

       python -m listings.fixtures.extract_images

2. Load fixtures and hydrate Photo.image_data from files:

       python manage.py load_listings_with_images

This command:
  - Optionally runs `loaddata` on the standard listings fixtures
    (statuses, property types, neighborhoods, price buckets, listings)
  - For each Photo record, looks for an image file named
        photo_<photo_id>.(png|jpg|jpeg|gif)
    in `listings/fixtures/images/` and writes its bytes into `image_data`.

Image files are not committed to source control; they are ignored via `.gitignore`.
Only the (now smaller) `listings/fixtures/listings.json` should be tracked.
"""

from __future__ import annotations

from pathlib import Path
import io

from django.conf import settings
from django.core.management import BaseCommand, call_command
from PIL import Image

from listings.models import Photo


class Command(BaseCommand):
    help = "Load listings fixtures and attach Photo.image_data from fixture image files."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--skip-loaddata",
            action="store_true",
            help="Skip loading fixtures and only (re)attach images.",
        )
        parser.add_argument(
            "--fixtures",
            nargs="*",
            help=(
                "Optional list of fixture paths to pass to loaddata. "
                "Defaults to the standard listings fixtures."
            ),
        )

    def handle(self, *args, **options) -> None:
        fixtures = options.get("fixtures") or [
            "listings/fixtures/statuses.json",
            "listings/fixtures/property_types.json",
            "listings/fixtures/neighborhoods.json",
            "listings/fixtures/pricebuckets.json",
            "listings/fixtures/listings.json",
        ]

        if not options.get("skip_loaddata"):
            self.stdout.write(
                self.style.NOTICE(f"Loading fixtures via loaddata: {', '.join(fixtures)}")
            )
            call_command("loaddata", *fixtures)

        base_dir = Path(settings.BASE_DIR)
        fixtures_dir = base_dir / "listings" / "fixtures"
        images_dir = fixtures_dir / "images"

        if not images_dir.exists():
            self.stdout.write(
                self.style.WARNING(f"Images directory not found: {images_dir}. Nothing to attach.")
            )
            return

        self.stdout.write(self.style.NOTICE(f"Attaching images from: {images_dir}"))

        updated = 0
        missing = 0

        for photo in Photo.objects.all():
            image_path = self._find_image_for_photo(images_dir, photo)
            if not image_path:
                missing += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"No image file found for Photo {photo.photo_id} "
                        f"(looked for photo_{photo.photo_id}.* or ISQA8210-Images/Listings/*)"
                    )
                )
                continue

            # Compress image bytes before storing to the database to keep the
            # overall fixture/data size manageable.
            photo.image_data = self._compress_image(image_path)
            photo.save(update_fields=["image_data"])
            updated += 1

        self.stdout.write(
            self.style.SUCCESS(f"Updated {updated} Photo records with image data.")
        )
        if missing:
            self.stdout.write(
                self.style.WARNING(f"Missing images for {missing} Photo records.")
            )

    @staticmethod
    def _compress_image(image_path: Path) -> bytes:
        """
        Open an image file, convert to RGB JPEG, optionally downscale,
        and return compressed bytes. Falls back to raw bytes on error.

        This implementation tries to keep the final size roughly under 50KB
        by downscaling and progressively lowering JPEG quality.
        """
        try:
            original_bytes = image_path.read_bytes()
            with Image.open(io.BytesIO(original_bytes)) as img:
                img = img.convert("RGB")
                # Downscale images to a maximum dimension to keep size small
                max_dim = 800
                img.thumbnail((max_dim, max_dim), Image.LANCZOS)

                target_size = 50 * 1024  # ~50 KB
                # Try a few quality levels, stopping once we're under target
                for quality in (60, 50, 40, 30):
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=quality, optimize=True)
                    data = buffer.getvalue()
                    if len(data) <= target_size or quality == 30:
                        return data
        except Exception:
            # If anything goes wrong, just store the original bytes
            return image_path.read_bytes()

    @staticmethod
    def _find_image_for_photo(images_dir: Path, photo: Photo) -> Path | None:
        """
        Return the path to the first matching image file for the given photo,
        or None if no file is found.
        """
        photo_id = photo.photo_id

        # 1) First, look for files named photo_<id>.* in the root images dir
        for ext in (".png", ".jpg", ".jpeg", ".gif"):
            candidate = images_dir / f"photo_{photo_id}{ext}"
            if candidate.exists():
                return candidate

        # 2) Fallback: use the ISQA8210-Images.zip directory structure.
        #    We derive the house number from the listing address and the
        #    photo_display_order to pick the correct image, e.g.:
        #      ISQA8210-Images/Listings/6317/6317-1.png
        try:
            address = (photo.listing.address or "").strip()
        except Exception:
            address = ""

        if address:
            house_num = address.split()[0]
        else:
            house_num = ""

        if house_num:
            listings_root = images_dir / "ISQA8210-Images" / "Listings" / house_num
            order = photo.photo_display_order or 1

            # Try numbered files like 6317-1.png, 6317-2.png, etc.
            for ext in (".png", ".jpg", ".jpeg", ".gif"):
                candidate = listings_root / f"{house_num}-{order}{ext}"
                if candidate.exists():
                    return candidate

            # Some listings may only have a single image like 7914.png
            for ext in (".png", ".jpg", ".jpeg", ".gif"):
                candidate = listings_root / f"{house_num}{ext}"
                if candidate.exists():
                    return candidate

        return None


