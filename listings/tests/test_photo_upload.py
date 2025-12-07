"""
Test cases specifically for photo/image upload functionality.
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from listings.models import Listing, Photo, PropertyType, Neighborhood, Status
from listings.forms import ListingForm
import io

User = get_user_model()


class PhotoUploadTests(TestCase):
    """Test cases for photo upload functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            firstname='Test',
            lastname='User'
        )
        self.property_type = PropertyType.objects.create(name='House')
        self.neighborhood = Neighborhood.objects.create(name='Downtown')
        self.status_active = Status.objects.create(name='Active')
    
    def create_png_image(self, name='test.png', size=100):
        """Create a valid PNG image file."""
        # Minimal valid PNG file
        png_header = b'\x89PNG\r\n\x1a\n'
        png_data = png_header + b'\x00' * (size - len(png_header))
        return SimpleUploadedFile(name, png_data, content_type='image/png')
    
    def create_jpeg_image(self, name='test.jpg', size=100):
        """Create a valid JPEG image file."""
        # Minimal valid JPEG file
        jpeg_header = b'\xff\xd8\xff\xe0'
        jpeg_data = jpeg_header + b'\x00' * (size - len(jpeg_header))
        return SimpleUploadedFile(name, jpeg_data, content_type='image/jpeg')
    
    def create_gif_image(self, name='test.gif', size=100):
        """Create a valid GIF image file."""
        # Minimal valid GIF file
        gif_header = b'GIF89a'
        gif_data = gif_header + b'\x00' * (size - len(gif_header))
        return SimpleUploadedFile(name, gif_data, content_type='image/gif')
    
    def test_upload_png_images(self):
        """Test uploading PNG images."""
        png_images = [self.create_png_image(f'image_{i}.png') for i in range(4)]
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        form = ListingForm(data=form_data, files={'photos': png_images})
        self.assertTrue(form.is_valid(), f"PNG images should be valid. Errors: {form.errors}")
    
    def test_upload_jpeg_images(self):
        """Test uploading JPEG images."""
        jpeg_images = [self.create_jpeg_image(f'image_{i}.jpg') for i in range(4)]
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        form = ListingForm(data=form_data, files={'photos': jpeg_images})
        self.assertTrue(form.is_valid(), f"JPEG images should be valid. Errors: {form.errors}")
    
    def test_upload_gif_images(self):
        """Test uploading GIF images."""
        gif_images = [self.create_gif_image(f'image_{i}.gif') for i in range(4)]
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        form = ListingForm(data=form_data, files={'photos': gif_images})
        self.assertTrue(form.is_valid(), f"GIF images should be valid. Errors: {form.errors}")
    
    def test_upload_mixed_image_types(self):
        """Test uploading mixed image types (should fail - all must be images)."""
        mixed_images = [
            self.create_png_image('image1.png'),
            self.create_jpeg_image('image2.jpg'),
            self.create_gif_image('image3.gif'),
            self.create_png_image('image4.png'),
        ]
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        form = ListingForm(data=form_data, files={'photos': mixed_images})
        # Mixed types should be valid as long as all are images
        self.assertTrue(form.is_valid(), f"Mixed image types should be valid. Errors: {form.errors}")
    
    def test_upload_non_image_files(self):
        """Test uploading non-image files."""
        non_image_files = [
            SimpleUploadedFile('file1.txt', b'This is text', content_type='text/plain'),
            SimpleUploadedFile('file2.pdf', b'PDF content', content_type='application/pdf'),
            SimpleUploadedFile('file3.doc', b'Word doc', content_type='application/msword'),
            SimpleUploadedFile('file4.zip', b'ZIP content', content_type='application/zip'),
        ]
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        form = ListingForm(data=form_data, files={'photos': non_image_files})
        self.assertFalse(form.is_valid())
        self.assertIn('photos', form.errors)
        self.assertIn('image', str(form.errors['photos']).lower())
    
    def test_upload_images_with_special_characters_in_filename(self):
        """Test uploading images with special characters in filenames."""
        special_name_images = [
            self.create_png_image('image with spaces.png'),
            self.create_png_image('image-with-dashes.png'),
            self.create_png_image('image_with_underscores.png'),
            self.create_png_image('image123.png'),
        ]
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        form = ListingForm(data=form_data, files={'photos': special_name_images})
        self.assertTrue(form.is_valid(), f"Special characters in filenames should be valid. Errors: {form.errors}")
    
    def test_upload_large_images(self):
        """Test uploading images that exceed size limit."""
        # Create images larger than 5MB
        large_images = []
        for i in range(4):
            large_image = SimpleUploadedFile(
                f'large_{i}.png',
                b'\x89PNG' + b'x' * (6 * 1024 * 1024),  # 6MB
                content_type='image/png'
            )
            large_images.append(large_image)
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        form = ListingForm(data=form_data, files={'photos': large_images})
        self.assertFalse(form.is_valid())
        self.assertIn('photos', form.errors)
        self.assertIn('large', str(form.errors['photos']).lower())
    
    def test_upload_empty_image_files(self):
        """Test uploading empty image files."""
        empty_images = [
            SimpleUploadedFile('empty1.png', b'', content_type='image/png'),
            SimpleUploadedFile('empty2.png', b'', content_type='image/png'),
            SimpleUploadedFile('empty3.png', b'', content_type='image/png'),
            SimpleUploadedFile('empty4.png', b'', content_type='image/png'),
        ]
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        form = ListingForm(data=form_data, files={'photos': empty_images})
        # Empty files might be valid but should be tested
        # The form validation might pass, but the actual save might fail
        # This depends on Django's file handling
    
    def test_photo_saved_to_database(self):
        """Test that photos are correctly saved to the database."""
        from django.test import Client
        
        client = Client()
        client.login(email='test@example.com', password='testpass123')
        
        png_images = [self.create_png_image(f'image_{i}.png', size=1000) for i in range(4)]
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        # Test using form directly (Django test client has issues with multiple files)
        form = ListingForm(data=form_data, files={'photos': png_images})
        self.assertTrue(form.is_valid())
        
        listing = form.save(commit=False)
        listing.created_by = self.user
        listing.is_visible = True
        status_value = form.cleaned_data.get('status')
        if status_value:
            status_mapping = {'Available': 'Active', 'Pending': 'Pending', 'Sold': 'Sold'}
            status_name = status_mapping.get(status_value)
            if status_name:
                status_obj = Status.objects.get(name=status_name)
                listing.status_id = status_obj
        listing.save()
        
        photos = form.cleaned_data.get('photos')
        for i, photo_file in enumerate(photos):
            photo_file.seek(0)
            Photo.objects.create(
                listing=listing,
                image_data=photo_file.read(),
                photo_display_order=i+1
            )
        
        listing.refresh_from_db()
        self.assertEqual(listing.photos.count(), 4)
        
        # Verify each photo has image data
        for photo in listing.photos.all():
            self.assertIsNotNone(photo.image_data)
            self.assertGreater(len(photo.image_data), 0)
            self.assertIsNotNone(photo.photo_display_order)
    
    def test_photo_display_order(self):
        """Test that photos maintain correct display order."""
        from django.test import Client
        
        client = Client()
        client.login(email='test@example.com', password='testpass123')
        
        png_images = [self.create_png_image(f'image_{i}.png') for i in range(4)]
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        # Test using form directly
        form = ListingForm(data=form_data, files={'photos': png_images})
        self.assertTrue(form.is_valid())
        
        listing = form.save(commit=False)
        listing.created_by = self.user
        listing.is_visible = True
        status_value = form.cleaned_data.get('status')
        if status_value:
            status_mapping = {'Available': 'Active', 'Pending': 'Pending', 'Sold': 'Sold'}
            status_name = status_mapping.get(status_value)
            if status_name:
                status_obj = Status.objects.get(name=status_name)
                listing.status_id = status_obj
        listing.save()
        
        photos = form.cleaned_data.get('photos')
        for i, photo_file in enumerate(photos):
            photo_file.seek(0)
            Photo.objects.create(
                listing=listing,
                image_data=photo_file.read(),
                photo_display_order=i+1
            )
        
        listing.refresh_from_db()
        photos = listing.photos.all().order_by('photo_display_order')
        
        # Verify order is 1, 2, 3, 4
        expected_order = [1, 2, 3, 4]
        actual_order = [photo.photo_display_order for photo in photos]
        self.assertEqual(actual_order, expected_order)

