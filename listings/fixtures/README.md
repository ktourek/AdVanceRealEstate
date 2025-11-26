# Fixtures Directory

## Listings Fixture and Images

The original `listings.json` fixture embedded base64-encoded `image_data` for
`listings.photo` records, making the file ~91MB and unsuitable for git.

The project now uses **separate image files** stored under
`listings/fixtures/images/`. The JSON fixture no longer contains `image_data`
fields; instead, photo binaries are hydrated from the image files after the
fixtures are loaded.

Image files in `listings/fixtures/images/` are **not committed** to git and are
ignored via `.gitignore`. Only the (much smaller) `listings.json` is intended
to be tracked.

### One-Time: Extract Images from Existing Fixture

If you have a local `listings.json` that still includes `image_data` for
`listings.photo` entries, you can extract the images and rewrite the fixture:

```bash
python -m listings.fixtures.extract_images
```

This will:

- Create `listings/fixtures/images/` (if needed)
- Decode each `image_data` field for `listings.photo` objects
- Save files as `photo_<photo_id>.<ext>` (PNG/JPEG/GIF detection)
- Remove `image_data` from the JSON
- Create a backup: `listings/fixtures/listings_with_images.backup.json`

After this step, `listings.json` no longer contains any embedded image data and
can be safely committed to the repository.

### Loading Fixtures with Images

To load all lookup data and listings, and then hydrate `Photo.image_data` from
the extracted image files, run:

```bash
python manage.py load_listings_with_images
```

By default, this command will:

1. Run `loaddata` on the standard fixtures:
   - `listings/fixtures/statuses.json`
   - `listings/fixtures/property_types.json`
   - `listings/fixtures/neighborhoods.json`
   - `listings/fixtures/pricebuckets.json`
   - `listings/fixtures/listings.json`
2. For each `Photo` record, look for an image file named:
   - `listings/fixtures/images/photo_<photo_id>.png|jpg|jpeg|gif`
3. If found, load the file bytes into `Photo.image_data`

If you have already loaded the JSON fixtures (for example, via a different
command), you can skip the `loaddata` step and only attach images:

```bash
python manage.py load_listings_with_images --skip-loaddata
```

You can also specify a custom set of fixture files to load:

```bash
python manage.py load_listings_with_images --fixtures \
  listings/fixtures/statuses.json \
  listings/fixtures/property_types.json \
  listings/fixtures/neighborhoods.json \
  listings/fixtures/pricebuckets.json \
  listings/fixtures/listings.json
```

The `listings/fixtures/images/` directory is kept in the repository only via a
`.gitkeep` file; the binary image files themselves remain local. This keeps the
repository size small while still allowing realistic photo data in development.

