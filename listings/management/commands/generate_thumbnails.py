"""
Management command to generate thumbnails for existing photos.

This command is useful for generating thumbnails for photos that were
uploaded before the thumbnail feature was implemented.

Usage:
    py manage.py generate_thumbnails
"""

from django.core.management.base import BaseCommand
from listings.models import Photo
from listings.image_utils import generate_thumbnail


class Command(BaseCommand):
    help = "Generate thumbnails for existing photos that don't have them"

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate thumbnails even if they already exist',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        if force:
            photos = Photo.objects.filter(image_data__isnull=False)
            self.stdout.write(
                self.style.NOTICE(f"Regenerating thumbnails for all {photos.count()} photos...")
            )
        else:
            photos = Photo.objects.filter(
                image_data__isnull=False,
                thumbnail_data__isnull=True
            )
            self.stdout.write(
                self.style.NOTICE(f"Generating thumbnails for {photos.count()} photos without thumbnails...")
            )
        
        if photos.count() == 0:
            self.stdout.write(
                self.style.SUCCESS("No photos need thumbnail generation.")
            )
            return
        
        success_count = 0
        error_count = 0
        
        for photo in photos:
            try:
                thumbnail = generate_thumbnail(photo.image_data)
                if thumbnail:
                    photo.thumbnail_data = thumbnail
                    photo.save(update_fields=['thumbnail_data'])
                    success_count += 1
                    self.stdout.write(f"Generated thumbnail for Photo {photo.photo_id}")
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"Failed to generate thumbnail for Photo {photo.photo_id}")
                    )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"Error processing Photo {photo.photo_id}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted: {success_count} thumbnails generated, {error_count} errors"
            )
        )
