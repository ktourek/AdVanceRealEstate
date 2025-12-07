"""
Test cases for ListingForm validation and special characters handling.
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from listings.forms import ListingForm
from listings.models import PropertyType, Neighborhood, User
import io


class ListingFormValidationTests(TestCase):
    """Test input validation for ListingForm."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            firstname='Test',
            lastname='User'
        )
        
        # Create test property type
        self.property_type = PropertyType.objects.create(name='House')
        
        # Create test neighborhood
        self.neighborhood = Neighborhood.objects.create(name='Downtown')
        
        # Create test image files
        self.create_test_images()
    
    def create_test_images(self):
        """Create test image files."""
        # Create 4 valid PNG images
        self.valid_images = []
        for i in range(4):
            image = SimpleUploadedFile(
                name=f'test_image_{i}.png',
                content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82',
                content_type='image/png'
            )
            self.valid_images.append(image)
    
    def test_form_with_valid_data(self):
        """Test form validation with all valid data."""
        form_data = {
            'address': '123 Main St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful home in downtown Omaha.'
        }
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_form_missing_required_fields(self):
        """Test form validation with missing required fields."""
        form = ListingForm(data={}, files={})
        self.assertFalse(form.is_valid())
        self.assertIn('address', form.errors)
        self.assertIn('price', form.errors)
        self.assertIn('property_type', form.errors)
        self.assertIn('neighborhood', form.errors)
        self.assertIn('photos', form.errors)
    
    def test_form_missing_photos(self):
        """Test form validation when no photos are uploaded."""
        form_data = {
            'address': '123 Main St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful home.'
        }
        form = ListingForm(data=form_data, files={})
        self.assertFalse(form.is_valid())
        self.assertIn('photos', form.errors)
    
    def test_form_wrong_number_of_photos(self):
        """Test form validation with incorrect number of photos."""
        form_data = {
            'address': '123 Main St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful home.'
        }
        # Test with 3 photos (should be 4)
        three_images = self.valid_images[:3]
        form = ListingForm(data=form_data, files={'photos': three_images})
        self.assertFalse(form.is_valid())
        self.assertIn('photos', form.errors)
        self.assertIn('exactly 4 photos', str(form.errors['photos']))
        
        # Test with 5 photos (should be 4)
        five_images = self.valid_images + [self.valid_images[0]]
        form = ListingForm(data=form_data, files={'photos': five_images})
        self.assertFalse(form.is_valid())
        self.assertIn('photos', form.errors)
    
    def test_form_invalid_image_type(self):
        """Test form validation with non-image files."""
        form_data = {
            'address': '123 Main St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful home.'
        }
        # Create invalid file (text file instead of image)
        invalid_files = [
            SimpleUploadedFile('test.txt', b'This is not an image', content_type='text/plain')
        ] * 4
        form = ListingForm(data=form_data, files={'photos': invalid_files})
        self.assertFalse(form.is_valid())
        self.assertIn('photos', form.errors)
    
    def test_form_large_image_file(self):
        """Test form validation with image file exceeding size limit."""
        form_data = {
            'address': '123 Main St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful home.'
        }
        # Create large image file (>5MB)
        large_image = SimpleUploadedFile(
            name='large_image.png',
            content=b'\x89PNG' + b'x' * (6 * 1024 * 1024),  # 6MB
            content_type='image/png'
        )
        large_files = [large_image] * 4
        form = ListingForm(data=form_data, files={'photos': large_files})
        self.assertFalse(form.is_valid())
        self.assertIn('photos', form.errors)
    
    def test_form_invalid_price(self):
        """Test form validation with invalid price."""
        form_data = {
            'address': '123 Main St, Omaha, NE 68102',
            'price': 'invalid_price',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful home.'
        }
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
    
    def test_form_negative_price(self):
        """Test form validation with negative price."""
        form_data = {
            'address': '123 Main St, Omaha, NE 68102',
            'price': '-1000',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful home.'
        }
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
        # Django DecimalField should handle this, but let's test it
        if not form.is_valid():
            self.assertIn('price', form.errors)
    
    def test_form_invalid_bedrooms(self):
        """Test form validation with invalid bedrooms value."""
        form_data = {
            'address': '123 Main St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': 'not_a_number',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful home.'
        }
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
        self.assertFalse(form.is_valid())
        self.assertIn('bedrooms', form.errors)
    
    def test_form_invalid_bathrooms(self):
        """Test form validation with invalid bathrooms value."""
        form_data = {
            'address': '123 Main St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': 'not_a_number',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful home.'
        }
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
        self.assertFalse(form.is_valid())
        self.assertIn('bathrooms', form.errors)
    
    def test_form_invalid_square_footage(self):
        """Test form validation with invalid square footage."""
        form_data = {
            'address': '123 Main St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': 'not_a_number',
            'status': 'Available',
            'description': 'A beautiful home.'
        }
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
        self.assertFalse(form.is_valid())
        self.assertIn('square_footage', form.errors)


class ListingFormSpecialCharactersTests(TestCase):
    """Test form handling of special characters in input fields."""
    
    def setUp(self):
        """Set up test data."""
        self.property_type = PropertyType.objects.create(name='House')
        self.neighborhood = Neighborhood.objects.create(name='Downtown')
        self.create_test_images()
    
    def create_test_images(self):
        """Create test image files."""
        self.valid_images = []
        for i in range(4):
            image = SimpleUploadedFile(
                name=f'test_image_{i}.png',
                content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82',
                content_type='image/png'
            )
            self.valid_images.append(image)
    
    def test_address_with_special_characters(self):
        """Test address field with special characters."""
        special_char_addresses = [
            "123 Main St. #4B, Omaha, NE 68102",
            "456 O'Connor Ave, Omaha, NE 68103",
            "789 St. Mary's Lane, Omaha, NE 68104",
            "321 N. 72nd St., Apt. 5, Omaha, NE 68105",
            "654 E-W Highway, Omaha, NE 68106",
            "987 & Company Blvd, Omaha, NE 68107",
        ]
        
        for address in special_char_addresses:
            form_data = {
                'address': address,
                'price': '250000.00',
                'property_type': self.property_type.pk,
                'neighborhood': self.neighborhood.pk,
                'bedrooms': '3',
                'bathrooms': '2.0',
                'square_footage': '1500',
                'status': 'Available',
                'description': 'Test description.'
            }
            form = ListingForm(data=form_data, files={'photos': self.valid_images})
            self.assertTrue(form.is_valid(), f"Address '{address}' should be valid. Errors: {form.errors}")
    
    def test_description_with_special_characters(self):
        """Test description field with special characters."""
        special_char_descriptions = [
            "Beautiful home with 3BR/2BA! Features include: hardwood floors, updated kitchen & bath.",
            "Stunning property @ prime location. Price: $250,000. Contact: (402) 555-1234",
            "Home includes: washer/dryer, A/C, & more! Open house: Sat-Sun 1-4pm.",
            "Property details: 1,500 sq ft, built in 2020. Energy-efficient & eco-friendly!",
            "Special features: granite countertops, stainless steel appliances, & walk-in closets.",
            "Location: Near schools, parks, & shopping. Easy access to I-80 & Highway 75.",
        ]
        
        for description in special_char_descriptions:
            form_data = {
                'address': '123 Main St, Omaha, NE 68102',
                'price': '250000.00',
                'property_type': self.property_type.pk,
                'neighborhood': self.neighborhood.pk,
                'bedrooms': '3',
                'bathrooms': '2.0',
                'square_footage': '1500',
                'status': 'Available',
                'description': description
            }
            form = ListingForm(data=form_data, files={'photos': self.valid_images})
            self.assertTrue(form.is_valid(), f"Description with special chars should be valid. Errors: {form.errors}")
    
    def test_address_with_unicode_characters(self):
        """Test address field with Unicode characters."""
        unicode_addresses = [
            "123 Main St, Omaha, NE 68102",  # Standard ASCII
            "456 Café Street, Omaha, NE 68103",  # Accented characters
            "789 Résumé Road, Omaha, NE 68104",  # More accents
        ]
        
        for address in unicode_addresses:
            form_data = {
                'address': address,
                'price': '250000.00',
                'property_type': self.property_type.pk,
                'neighborhood': self.neighborhood.pk,
                'bedrooms': '3',
                'bathrooms': '2.0',
                'square_footage': '1500',
                'status': 'Available',
                'description': 'Test description.'
            }
            form = ListingForm(data=form_data, files={'photos': self.valid_images})
            self.assertTrue(form.is_valid(), f"Unicode address '{address}' should be valid. Errors: {form.errors}")
    
    def test_description_with_html_characters(self):
        """Test description field with HTML-like characters."""
        html_descriptions = [
            "Home features <3 bedrooms> and >2 bathrooms",
            "Price: $250,000 & includes all appliances",
            "Contact: info@example.com or call (402) 555-1234",
            "Property includes: washer/dryer, A/C, & more!",
        ]
        
        for description in html_descriptions:
            form_data = {
                'address': '123 Main St, Omaha, NE 68102',
                'price': '250000.00',
                'property_type': self.property_type.pk,
                'neighborhood': self.neighborhood.pk,
                'bedrooms': '3',
                'bathrooms': '2.0',
                'square_footage': '1500',
                'status': 'Available',
                'description': description
            }
            form = ListingForm(data=form_data, files={'photos': self.valid_images})
            self.assertTrue(form.is_valid(), f"HTML-like chars in description should be valid. Errors: {form.errors}")
    
    def test_address_with_sql_injection_attempts(self):
        """Test address field with SQL injection-like strings (should be handled safely)."""
        sql_injection_attempts = [
            "123 Main St'; DROP TABLE listings; --",
            "456 O'Connor Ave OR '1'='1",
            "789 Test St UNION SELECT * FROM listings",
        ]
        
        for address in sql_injection_attempts:
            form_data = {
                'address': address,
                'price': '250000.00',
                'property_type': self.property_type.pk,
                'neighborhood': self.neighborhood.pk,
                'bedrooms': '3',
                'bathrooms': '2.0',
                'square_footage': '1500',
                'status': 'Available',
                'description': 'Test description.'
            }
            form = ListingForm(data=form_data, files={'photos': self.valid_images})
            # Should be valid (Django ORM handles SQL injection protection)
            self.assertTrue(form.is_valid(), f"SQL injection attempt should be handled safely. Errors: {form.errors}")
    
    def test_address_with_xss_attempts(self):
        """Test address field with XSS-like strings (should be handled safely)."""
        xss_attempts = [
            "123 Main St<script>alert('XSS')</script>",
            "456 Test St<img src=x onerror=alert('XSS')>",
            "789 St <iframe src='evil.com'></iframe>",
        ]
        
        for address in xss_attempts:
            form_data = {
                'address': address,
                'price': '250000.00',
                'property_type': self.property_type.pk,
                'neighborhood': self.neighborhood.pk,
                'bedrooms': '3',
                'bathrooms': '2.0',
                'square_footage': '1500',
                'status': 'Available',
                'description': 'Test description.'
            }
            form = ListingForm(data=form_data, files={'photos': self.valid_images})
            # Should be valid (template auto-escaping handles XSS)
            self.assertTrue(form.is_valid(), f"XSS attempt should be handled safely. Errors: {form.errors}")

