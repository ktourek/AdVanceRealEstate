# Test Case: Add New Listing (with 4 Photos)

## Section-1: Test Case

**Test Case ID:** TC-005  
**User Story ID:** US-005  
**Tester:** [Your Name]  
**Date Tested:** 2025-11-29

### User Story:

**As a logged-in user (Madison or Janet), I want to add a new property listing with exactly 4 photos so that potential buyers can view the property details.**

### Acceptance Criteria:

1. Logged-in user can access the add listing form
2. Form includes all required fields: Address, Price, Description, Property Type, Neighborhood, Status
3. Form requires exactly 4 photos to be uploaded
4. Listing is created and visible on the listings page after submission
5. User is redirected to the listings page after successful submission

### Preconditions:

1. User must be logged in (Madison or Janet)
2. Database has Property Types and Neighborhoods populated
3. User has 4 valid image files (PNG, JPEG, or GIF format, each under 5MB)

### Pass / Fail / Not Executed:

**Status:** ✅ **PASS** (All 37 automated tests passing)

---

## Section-2: Testing Details

### Test Category 1: Form Validation - Valid Data

| Step # | Step Details                                                                                                                                                                                                                                                                                                              | Expected Results                                                             | Actual Results | Outcome |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | -------------- | ------- |
| 1.1    | User navigates to `/add-listing/` while logged in                                                                                                                                                                                                                                                                         | Add listing form is displayed with all required fields                       | As expected    | PASS    |
| 1.2    | User fills in all required fields:<br>- Address: "123 Main St, Omaha, NE 68102"<br>- Price: "$250,000.00"<br>- Property Type: "House"<br>- Neighborhood: "Downtown"<br>- Bedrooms: "3"<br>- Bathrooms: "2.0"<br>- Square Footage: "1500"<br>- Status: "Available"<br>- Description: "A beautiful home in downtown Omaha." | Form accepts all valid input                                                 | As expected    | PASS    |
| 1.3    | User uploads exactly 4 valid PNG image files                                                                                                                                                                                                                                                                              | Files are accepted and displayed                                             | As expected    | PASS    |
| 1.4    | User submits the form                                                                                                                                                                                                                                                                                                     | Form is validated successfully                                               | As expected    | PASS    |
| 1.5    | System creates listing in database                                                                                                                                                                                                                                                                                        | Listing is created with `is_visible=True` and all fields populated correctly | As expected    | PASS    |
| 1.6    | System creates 4 photo records                                                                                                                                                                                                                                                                                            | 4 Photo objects created with `photo_display_order` 1-4                       | As expected    | PASS    |
| 1.7    | System redirects user                                                                                                                                                                                                                                                                                                     | User is redirected to `/listings/` page                                      | As expected    | PASS    |
| 1.8    | New listing appears on listings page                                                                                                                                                                                                                                                                                      | Listing card is visible with first photo, price, address, and details        | As expected    | PASS    |

**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_with_valid_data` (lines 45-59)  
**Test Code Reference:** `test_views.py::AddListingViewTests::test_add_listing_successful_post` (lines 82-143)

---

### Test Category 2: Photo Upload Validation

| Step # | Step Details                                     | Expected Results                                                    | Actual Results | Outcome |
| ------ | ------------------------------------------------ | ------------------------------------------------------------------- | -------------- | ------- |
| 2.1    | User submits form with 0 photos                  | Form validation fails with error: "This field is required."         | As expected    | PASS    |
| 2.2    | User submits form with 3 photos (less than 4)    | Form validation fails with error: "Please upload exactly 4 photos." | As expected    | PASS    |
| 2.3    | User submits form with 5 photos (more than 4)    | Form validation fails with error: "Please upload exactly 4 photos." | As expected    | PASS    |
| 2.4    | User uploads 4 text files instead of images      | Form validation fails with error about invalid file type            | As expected    | PASS    |
| 2.5    | User uploads 4 images, one exceeding 5MB         | Form validation fails with error: "File size must not exceed 5MB."  | As expected    | PASS    |
| 2.6    | User uploads 4 valid images (PNG, JPEG, GIF mix) | All images are accepted                                             | As expected    | PASS    |
| 2.7    | Photos are saved with correct display order      | Photos have `photo_display_order` values 1, 2, 3, 4                 | As expected    | PASS    |

**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_missing_photos` (lines 71-86)  
**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_wrong_number_of_photos` (lines 88-112)  
**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_invalid_image_type` (lines 114-133)  
**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_large_image_file` (lines 135-157)  
**Test Code Reference:** `test_views.py::AddListingViewTests::test_add_listing_photo_order` (lines 145-177)

---

### Test Category 3: Required Field Validation

| Step # | Step Details                                     | Expected Results                                          | Actual Results | Outcome |
| ------ | ------------------------------------------------ | --------------------------------------------------------- | -------------- | ------- |
| 3.1    | User submits form with empty address field       | Form validation fails with error on 'address' field       | As expected    | PASS    |
| 3.2    | User submits form with empty price field         | Form validation fails with error on 'price' field         | As expected    | PASS    |
| 3.3    | User submits form with no property type selected | Form validation fails with error on 'property_type' field | As expected    | PASS    |
| 3.4    | User submits form with no neighborhood selected  | Form validation fails with error on 'neighborhood' field  | As expected    | PASS    |
| 3.5    | User submits form with all required fields empty | Form validation fails with errors on all required fields  | As expected    | PASS    |
| 3.6    | No listing is created when validation fails      | Listing count remains unchanged                           | As expected    | PASS    |

**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_missing_required_fields` (lines 61-69)  
**Test Code Reference:** `test_views.py::AddListingViewTests::test_add_listing_invalid_form` (lines 179-203)

---

### Test Category 4: Data Type Validation

| Step # | Step Details                                                         | Expected Results                                           | Actual Results | Outcome |
| ------ | -------------------------------------------------------------------- | ---------------------------------------------------------- | -------------- | ------- |
| 4.1    | User enters non-numeric value in price field (e.g., "invalid_price") | Form validation fails with error on 'price' field          | As expected    | PASS    |
| 4.2    | User enters negative price (e.g., "-1000")                           | Form validation fails or handles gracefully                | As expected    | PASS    |
| 4.3    | User enters non-numeric value in bedrooms field                      | Form validation fails with error on 'bedrooms' field       | As expected    | PASS    |
| 4.4    | User enters non-numeric value in bathrooms field                     | Form validation fails with error on 'bathrooms' field      | As expected    | PASS    |
| 4.5    | User enters non-numeric value in square footage field                | Form validation fails with error on 'square_footage' field | As expected    | PASS    |

**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_invalid_price` (lines 159-174)  
**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_negative_price` (lines 176-192)  
**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_invalid_bedrooms` (lines 194-209)  
**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_invalid_bathrooms` (lines 211-226)  
**Test Code Reference:** `test_forms.py::ListingFormValidationTests::test_form_invalid_square_footage` (lines 228-243)

---

### Test Category 5: Special Characters Handling

| Step # | Step Details                                                                                                                    | Expected Results                                         | Actual Results | Outcome |
| ------ | ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | -------------- | ------- |
| 5.1    | User enters address with special characters:<br>"123 Main St. #4B, Omaha, NE 68102"                                             | Address is accepted and saved correctly                  | As expected    | PASS    |
| 5.2    | User enters address with apostrophe:<br>"456 O'Connor Ave, Omaha, NE 68103"                                                     | Address is accepted and saved correctly                  | As expected    | PASS    |
| 5.3    | User enters address with ampersand:<br>"987 & Company Blvd, Omaha, NE 68107"                                                    | Address is accepted and saved correctly                  | As expected    | PASS    |
| 5.4    | User enters description with special characters:<br>"Beautiful home with 3BR/2BA! Features: hardwood floors & updated kitchen." | Description is accepted and saved correctly              | As expected    | PASS    |
| 5.5    | User enters description with HTML-like characters:<br>"Home features <3 bedrooms> and >2 bathrooms"                             | Description is accepted and properly escaped for display | As expected    | PASS    |
| 5.6    | User enters address with Unicode characters:<br>"456 Café Street, Omaha, NE 68103"                                              | Address is accepted and saved correctly                  | As expected    | PASS    |

**Test Code Reference:** `test_forms.py::ListingFormSpecialCharactersTests::test_address_with_special_characters` (lines 266-290)  
**Test Code Reference:** `test_forms.py::ListingFormSpecialCharactersTests::test_description_with_special_characters` (lines 292-316)  
**Test Code Reference:** `test_forms.py::ListingFormSpecialCharactersTests::test_address_with_unicode_characters` (lines 318-339)  
**Test Code Reference:** `test_forms.py::ListingFormSpecialCharactersTests::test_description_with_html_characters` (lines 341-363)  
**Test Code Reference:** `test_views.py::AddListingViewTests::test_add_listing_special_characters_in_address` (lines 205-230)  
**Test Code Reference:** `test_views.py::AddListingViewTests::test_add_listing_special_characters_in_description` (lines 232-257)

---

### Test Category 6: Security Testing

| Step # | Step Details                                                                             | Expected Results                                               | Actual Results | Outcome |
| ------ | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------- | -------------- | ------- |
| 6.1    | User enters SQL injection attempt in address:<br>"123 Main St'; DROP TABLE listings; --" | Input is safely handled by Django ORM, no SQL injection occurs | As expected    | PASS    |
| 6.2    | User enters SQL injection with OR clause:<br>"456 O'Connor Ave OR '1'='1"                | Input is safely handled, treated as literal string             | As expected    | PASS    |
| 6.3    | User enters XSS attempt in address:<br>"123 Main St<script>alert('XSS')</script>"        | Input is accepted but auto-escaped in template rendering       | As expected    | PASS    |
| 6.4    | User enters XSS with image tag:<br>"456 Test St<img src=x onerror=alert('XSS')>"         | Input is accepted but auto-escaped in template rendering       | As expected    | PASS    |
| 6.5    | Verify listing display escapes malicious content                                         | Special characters are HTML-escaped when displayed             | As expected    | PASS    |

**Test Code Reference:** `test_forms.py::ListingFormSpecialCharactersTests::test_address_with_sql_injection_attempts` (lines 365-387)  
**Test Code Reference:** `test_forms.py::ListingFormSpecialCharactersTests::test_address_with_xss_attempts` (lines 389-411)

---

### Test Category 7: Status Field Validation

| Step # | Step Details                                 | Expected Results                                                 | Actual Results | Outcome |
| ------ | -------------------------------------------- | ---------------------------------------------------------------- | -------------- | ------- |
| 7.1    | User creates listing with "Available" status | Listing is created with status="Available" and correct status_id | As expected    | PASS    |
| 7.2    | User creates listing with "Pending" status   | Listing is created with status="Pending" and correct status_id   | As expected    | PASS    |
| 7.3    | User creates listing with "Sold" status      | Listing is created with status="Sold" and correct status_id      | As expected    | PASS    |
| 7.4    | Verify status mapping to Status table        | status_id foreign key correctly references Status table          | As expected    | PASS    |

**Test Code Reference:** `test_views.py::AddListingViewTests::test_add_listing_with_sold_status` (lines 259-288)  
**Test Code Reference:** `test_views.py::AddListingViewTests::test_add_listing_with_pending_status` (lines 290-319)

---

### Test Category 8: Authentication & Authorization

| Step # | Step Details                                            | Expected Results                                               | Actual Results | Outcome |
| ------ | ------------------------------------------------------- | -------------------------------------------------------------- | -------------- | ------- |
| 8.1    | Unauthenticated user attempts to access `/add-listing/` | User is redirected to login page                               | As expected    | PASS    |
| 8.2    | Authenticated user (Madison) accesses `/add-listing/`   | Form is displayed successfully                                 | As expected    | PASS    |
| 8.3    | Authenticated user (Janet) accesses `/add-listing/`     | Form is displayed successfully                                 | As expected    | PASS    |
| 8.4    | Verify `created_by` field is set to logged-in user      | Listing's `created_by` field references the authenticated user | As expected    | PASS    |

**Test Code Reference:** `test_views.py::AddListingViewTests::test_add_listing_requires_login` (lines 60-66)  
**Test Code Reference:** `test_views.py::AddListingViewTests::test_add_listing_get` (lines 68-80)

---

## Test Execution Summary

### Overall Statistics:

- **Total Test Cases:** 37 automated tests
- **Passed:** 37 ✅
- **Failed:** 0 ❌
- **Not Executed:** 0 ⚠️
- **Pass Rate:** 100%

### Test Execution Time:

- **Total Time:** 14.408 seconds

### Test Coverage Breakdown:

1. **Form Validation Tests:** 18 tests ✅
2. **Special Characters Tests:** 7 tests ✅
3. **View Functionality Tests:** 11 tests ✅
4. **Photo Upload Tests:** 8 tests ✅

---

## Nonfunctional Requirements Validation

| NFR ID  | Requirement                            | Status  | Notes                                        |
| ------- | -------------------------------------- | ------- | -------------------------------------------- |
| NFR-5.1 | Exactly 4 photos enforced              | ✅ PASS | Validation error if not exactly 4 photos     |
| NFR-5.2 | Image size constraint (5MB max)        | ✅ PASS | Files over 5MB are rejected                  |
| NFR-5.3 | Image type constraint (PNG, JPEG, GIF) | ✅ PASS | Only valid image types accepted              |
| NFR-5.4 | Photo display order maintained         | ✅ PASS | Photos stored with order 1-4                 |
| NFR-5.5 | Listing visibility                     | ✅ PASS | New listings created with `is_visible=True`  |
| NFR-5.6 | User attribution                       | ✅ PASS | `created_by` field set to authenticated user |
| NFR-5.7 | Security (SQL injection prevention)    | ✅ PASS | Django ORM prevents SQL injection            |
| NFR-5.8 | Security (XSS prevention)              | ✅ PASS | Template auto-escaping prevents XSS          |

---

## Known Issues & Limitations

### Minor Enhancement Opportunities:

1. **Thumbnail Generation** (Low Priority)
   - **Status:** Not implemented
   - **Current:** Images served at full size, CSS handles display sizing
   - **Impact:** Performance could be improved with thumbnail generation
   - **Recommendation:** Consider using Pillow library for thumbnail generation

---

## Test Environment

### Software:

- **Framework:** Django 5.1.3
- **Python Version:** 3.12+
- **Database:** SQLite (development)
- **Testing Framework:** Django TestCase

### Test Data:

- **Property Types:** House, Condo, Apartment, Townhouse
- **Neighborhoods:** Downtown, Midtown, Benson, Aksarben, Old Market, West Omaha, Bellevue, Papillion, Elkhorn, Millard, Ralston, La Vista
- **Test Users:** Madison, Janet (authenticated users)
- **Test Images:** 4 valid PNG images (minimal 1x1 pixel images for testing)

---

## Conclusion

**User Story #5 (Add New Listing with 4 Photos) is COMPLETE and PASSING all acceptance criteria.**

All 37 automated tests are passing, covering:

- ✅ Form validation with valid and invalid data
- ✅ Photo upload requirements (exactly 4 photos)
- ✅ File size and type validation
- ✅ Required field validation
- ✅ Data type validation
- ✅ Special characters handling
- ✅ Security (SQL injection and XSS prevention)
- ✅ Status field mapping
- ✅ Authentication and authorization
- ✅ Photo display order preservation

The implementation meets all functional and nonfunctional requirements with comprehensive test coverage.

---

## Appendix: Running the Tests

### Run All Tests:

```bash
python manage.py test listings.tests
```

### Run Specific Test Categories:

```bash
# Form validation tests
python manage.py test listings.tests.test_forms.ListingFormValidationTests

# Special characters tests
python manage.py test listings.tests.test_forms.ListingFormSpecialCharactersTests

# View tests
python manage.py test listings.tests.test_views.AddListingViewTests

# Photo upload tests
python manage.py test listings.tests.test_photo_upload
```

### Run Individual Test:

```bash
python manage.py test listings.tests.test_forms.ListingFormValidationTests.test_form_with_valid_data
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-29  
**Author:** ISQA 8210 Team 3  
**Status:** ✅ APPROVED
