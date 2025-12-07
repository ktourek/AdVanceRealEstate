# Listings App Test Suite

This directory contains comprehensive test cases for the listings app, specifically focusing on the "Add Listing" feature.

## Test Structure

### `test_forms.py`
Tests for form validation and special characters handling:
- **Input Validation Tests**: Tests for required fields, data types, and field validation
- **Special Characters Tests**: Tests for handling special characters, Unicode, HTML-like strings, SQL injection attempts, and XSS attempts in address and description fields

### `test_views.py`
Tests for the add_listing view functionality:
- View access and authentication requirements
- Successful listing creation
- Status mapping (Available → Active, Pending → Pending, Sold → Sold)
- Form error handling
- Redirect behavior after successful submission

### `test_photo_upload.py`
Tests specifically for photo/image upload functionality:
- Different image formats (PNG, JPEG, GIF)
- Mixed image types
- Non-image file rejection
- File size limits
- Special characters in filenames
- Photo storage and display order

## Running the Tests

### Run all tests:
```bash
python manage.py test listings.tests
```

### Run specific test file:
```bash
python manage.py test listings.tests.test_forms
python manage.py test listings.tests.test_views
python manage.py test listings.tests.test_photo_upload
```

### Run specific test class:
```bash
python manage.py test listings.tests.test_forms.ListingFormValidationTests
python manage.py test listings.tests.test_forms.ListingFormSpecialCharactersTests
```

### Run specific test method:
```bash
python manage.py test listings.tests.test_forms.ListingFormValidationTests.test_form_with_valid_data
```

### Run with verbose output:
```bash
python manage.py test listings.tests --verbosity=2
```

## Test Coverage

The test suite covers:

1. **Form Validation**
   - Required fields
   - Data type validation
   - Field-specific validation (price, bedrooms, bathrooms, square_footage)
   - Photo upload requirements (exactly 4 images)
   - Image type validation
   - File size limits

2. **Special Characters**
   - Address field: apostrophes, periods, hash symbols, ampersands, hyphens
   - Description field: various punctuation, HTML-like characters
   - Unicode characters
   - Security: SQL injection and XSS attempt handling

3. **View Functionality**
   - Authentication requirements
   - Successful listing creation
   - Status mapping to status_id ForeignKey
   - Photo creation and ordering
   - Redirect behavior

4. **Photo Upload**
   - Multiple image formats (PNG, JPEG, GIF)
   - File validation
   - Size limits
   - Storage in database
   - Display order preservation

## Test Data Setup

Each test class includes a `setUp()` method that creates:
- Test user
- Property types
- Neighborhoods
- Status objects
- Test image files

## Notes

- All tests use Django's TestCase which provides database transaction rollback
- Test images are minimal valid image files created programmatically
- Tests verify both form validation and database persistence
- Security tests verify that Django's built-in protections handle SQL injection and XSS attempts safely

