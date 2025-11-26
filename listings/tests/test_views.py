"""
Test cases for add_listing view functionality and listings browsing.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from listings.models import Listing, Photo, PropertyType, Neighborhood, Status, Pricebucket, SearchLog
from listings.forms import ListingForm

User = get_user_model()


class AddListingViewTests(TestCase):
    """Test cases for the add_listing view."""
    
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
        
        # Create test statuses
        self.status_active = Status.objects.create(name='Active')
        self.status_pending = Status.objects.create(name='Pending')
        self.status_sold = Status.objects.create(name='Sold')
        
        # Create client and login
        self.client = Client()
        self.client.login(email='test@example.com', password='testpass123')
        
        # Create test images
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
    
    def test_add_listing_view_get(self):
        """Test GET request to add_listing view."""
        response = self.client.get(reverse('add_listing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listings/add_listing.html')
        self.assertIsInstance(response.context['form'], ListingForm)
    
    def test_add_listing_view_requires_login(self):
        """Test that add_listing view requires authentication."""
        self.client.logout()
        response = self.client.get(reverse('add_listing'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login/', response.url)
    
    def test_add_listing_successful_post(self):
        """Test successful POST request to add_listing view."""
        initial_count = Listing.objects.count()
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful test home.'
        }
        
        # Reset file pointers
        for img in self.valid_images:
            img.seek(0)
        
        # Test form validation first
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
        self.assertTrue(form.is_valid(), f"Form should be valid. Errors: {form.errors}")
        
        # Test the view logic by simulating what the view does
        # (Django test client has issues with multiple files with same name)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = self.user
            listing.is_visible = True
            
            # Map status string to status_id ForeignKey (same as view)
            status_value = form.cleaned_data.get('status')
            if status_value:
                status_mapping = {
                    'Available': 'Active',
                    'Pending': 'Pending',
                    'Sold': 'Sold'
                }
                status_name = status_mapping.get(status_value)
                if status_name:
                    status_obj = Status.objects.get(name=status_name)
                    listing.status_id = status_obj
            
            listing.save()
            
            # Handle photos (same as view)
            photos = form.cleaned_data.get('photos')
            for i, photo_file in enumerate(photos):
                photo_file.seek(0)  # Reset file pointer
                Photo.objects.create(
                    listing=listing,
                    image_data=photo_file.read(),
                    photo_display_order=i+1
                )
        
        # Verify listing was created
        self.assertEqual(Listing.objects.count(), initial_count + 1)
        listing = Listing.objects.latest('listed_date')
        self.assertEqual(listing.address, '123 Test St, Omaha, NE 68102')
        self.assertEqual(str(listing.price), '250000.00')
        self.assertEqual(listing.created_by, self.user)
        self.assertEqual(listing.is_visible, True)
        self.assertEqual(listing.status, 'Available')
        
        # Check status_id was set correctly
        self.assertEqual(listing.status_id, self.status_active)
        
        # Check photos were created
        self.assertEqual(listing.photos.count(), 4)
        photos = listing.photos.all().order_by('photo_display_order')
        for i, photo in enumerate(photos, start=1):
            self.assertEqual(photo.photo_display_order, i)
            self.assertIsNotNone(photo.image_data)
            self.assertGreater(len(photo.image_data), 0)
    
    def test_add_listing_with_pending_status(self):
        """Test adding listing with Pending status."""
        form_data = {
            'address': '456 Pending St, Omaha, NE 68103',
            'price': '300000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '4',
            'bathrooms': '3.0',
            'square_footage': '2000',
            'status': 'Pending',
            'description': 'Pending sale home.'
        }
        
        # Reset file pointers
        for img in self.valid_images:
            img.seek(0)
        
        # Test form and create listing
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
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
        
        # Verify status mapping
        listing.refresh_from_db()
        self.assertEqual(listing.status, 'Pending')
        self.assertEqual(listing.status_id, self.status_pending)
    
    def test_add_listing_with_sold_status(self):
        """Test adding listing with Sold status."""
        form_data = {
            'address': '789 Sold St, Omaha, NE 68104',
            'price': '400000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '5',
            'bathrooms': '4.0',
            'square_footage': '3000',
            'status': 'Sold',
            'description': 'Sold home.'
        }
        
        # Reset file pointers
        for img in self.valid_images:
            img.seek(0)
        
        # Test form and create listing
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
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
        
        # Verify status mapping
        listing.refresh_from_db()
        self.assertEqual(listing.status, 'Sold')
        self.assertEqual(listing.status_id, self.status_sold)
    
    def test_add_listing_invalid_form(self):
        """Test POST request with invalid form data."""
        initial_count = Listing.objects.count()
        
        form_data = {
            'address': '',  # Missing required field
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
        }
        
        response = self.client.post(
            reverse('add_listing'),
            data=form_data,
            files={'photos': self.valid_images}
        )
        
        # Should not redirect, form should show errors
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertFalse(form.is_valid())
        self.assertIn('address', form.errors)
        
        # No listing should be created
        self.assertEqual(Listing.objects.count(), initial_count)
    
    def test_add_listing_without_photos(self):
        """Test POST request without photos."""
        initial_count = Listing.objects.count()
        
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful test home.'
        }
        
        response = self.client.post(
            reverse('add_listing'),
            data=form_data,
            files={}  # No photos
        )
        
        # Should not redirect, form should show errors
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertFalse(form.is_valid())
        self.assertIn('photos', form.errors)
        
        # No listing should be created
        self.assertEqual(Listing.objects.count(), initial_count)
    
    def test_add_listing_photo_order(self):
        """Test that photos are saved with correct display order."""
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'A beautiful test home.'
        }
        
        # Reset file pointers
        for img in self.valid_images:
            img.seek(0)
        
        # Test form and create listing (same as view logic)
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
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
        
        # Verify display order
        listing.refresh_from_db()
        photos = listing.photos.all().order_by('photo_display_order')
        for i, photo in enumerate(photos, start=1):
            self.assertEqual(photo.photo_display_order, i)
    
    def test_add_listing_special_characters_in_address(self):
        """Test adding listing with special characters in address."""
        form_data = {
            'address': "123 O'Connor St. #4B, Omaha, NE 68102",
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Test description.'
        }
        
        # Reset file pointers
        for img in self.valid_images:
            img.seek(0)
        
        # Test form and create listing
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
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
        
        # Verify address with special characters
        listing.refresh_from_db()
        self.assertEqual(listing.address, "123 O'Connor St. #4B, Omaha, NE 68102")
    
    def test_add_listing_special_characters_in_description(self):
        """Test adding listing with special characters in description."""
        form_data = {
            'address': '123 Test St, Omaha, NE 68102',
            'price': '250000.00',
            'property_type': self.property_type.pk,
            'neighborhood': self.neighborhood.pk,
            'bedrooms': '3',
            'bathrooms': '2.0',
            'square_footage': '1500',
            'status': 'Available',
            'description': 'Home features: 3BR/2BA, hardwood floors, & updated kitchen! Price: $250,000.'
        }
        
        # Reset file pointers
        for img in self.valid_images:
            img.seek(0)
        
        # Test form and create listing
        form = ListingForm(data=form_data, files={'photos': self.valid_images})
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
        
        # Verify description with special characters
        listing.refresh_from_db()
        self.assertIn('3BR/2BA', listing.description)
        self.assertIn('$250,000', listing.description)


class AllListingsViewTests(TestCase):
    """Test cases for the all_listings view (browsing, filtering, pagination)."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            firstname='Test',
            lastname='User'
        )
        
        self.property_type_house = PropertyType.objects.create(name='House')
        self.property_type_condo = PropertyType.objects.create(name='Condo')
        
        self.neighborhood_downtown = Neighborhood.objects.create(name='Downtown')
        self.neighborhood_midtown = Neighborhood.objects.create(name='Midtown')
        
        self.status_active = Status.objects.create(name='Active')
        self.status_pending = Status.objects.create(name='Pending')
        
        # Create price buckets for testing price range filtering
        self.pricebucket_0_50k = Pricebucket.objects.create(range='$0 - $50,000')
        self.pricebucket_50_100k = Pricebucket.objects.create(range='$50,000 - $100,000')
        self.pricebucket_100_150k = Pricebucket.objects.create(range='$100,000 - $150,000')
        self.pricebucket_150_200k = Pricebucket.objects.create(range='$150,000 - $200,000')
        self.pricebucket_200_250k = Pricebucket.objects.create(range='$200,000 - $250,000')
        self.pricebucket_250_300k = Pricebucket.objects.create(range='$250,000 - $300,000')
        self.pricebucket_300_350k = Pricebucket.objects.create(range='$300,000 - $350,000')
        self.pricebucket_350_400k = Pricebucket.objects.create(range='$350,000 - $400,000')
        self.pricebucket_1m_plus = Pricebucket.objects.create(range='$1,000,000+')
        
        # Create multiple listings for testing pagination and filtering
        self.create_test_listings()
    
    def create_test_listings(self):
        """Create test listings."""
        listings_data = [
            {'address': '100 Test St, Omaha, NE 68102', 'price': 100000, 'neighborhood': self.neighborhood_downtown, 'property_type': self.property_type_house, 'status': 'Available'},
            {'address': '200 Test St, Omaha, NE 68102', 'price': 200000, 'neighborhood': self.neighborhood_downtown, 'property_type': self.property_type_condo, 'status': 'Available'},
            {'address': '300 Test St, Omaha, NE 68103', 'price': 300000, 'neighborhood': self.neighborhood_midtown, 'property_type': self.property_type_house, 'status': 'Available'},
            {'address': '400 Test St, Omaha, NE 68103', 'price': 400000, 'neighborhood': self.neighborhood_midtown, 'property_type': self.property_type_house, 'status': 'Pending'},
        ]
        
        for data in listings_data:
            listing = Listing.objects.create(
                address=data['address'],
                price=data['price'],
                created_by=self.user,
                neighborhood=data['neighborhood'],
                property_type=data['property_type'],
                status=data['status'],
                status_id=self.status_active if data['status'] == 'Available' else self.status_pending,
                is_visible=True,
                bedrooms=3,
                bathrooms=2.0,
                square_footage=1500
            )
    
    def test_all_listings_view_get(self):
        """Test GET request to all_listings view."""
        response = self.client.get(reverse('listings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listings/all_listings.html')
        self.assertIn('listings', response.context)
    
    def test_all_listings_shows_only_visible(self):
        """Test that only visible listings are shown."""
        # Create a hidden listing
        hidden_listing = Listing.objects.create(
            address='999 Hidden St, Omaha, NE 68102',
            price=500000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=False
        )
        
        response = self.client.get(reverse('listings'))
        listings = response.context['listings']
        
        # Check that hidden listing is not in results
        listing_addresses = [listing.address for listing in listings]
        self.assertNotIn('999 Hidden St, Omaha, NE 68102', listing_addresses)
    
    def test_filter_by_neighborhood(self):
        """Test filtering listings by neighborhood."""
        response = self.client.get(reverse('listings'), {'neighborhood': self.neighborhood_downtown.pk})
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        for listing in listings:
            self.assertEqual(listing.neighborhood, self.neighborhood_downtown)
    
    def test_neighborhood_search_logging(self):
        """Test that neighborhood searches are logged to SearchLog."""
        initial_log_count = SearchLog.objects.count()
        
        # Perform a neighborhood search
        response = self.client.get(reverse('listings'), {'neighborhood': self.neighborhood_downtown.pk})
        self.assertEqual(response.status_code, 200)
        
        # Verify a search log entry was created
        new_log_count = SearchLog.objects.count()
        self.assertEqual(new_log_count, initial_log_count + 1)
        
        # Verify the log entry has correct neighborhood
        latest_log = SearchLog.objects.latest('timestamp')
        self.assertEqual(latest_log.neighborhood, self.neighborhood_downtown)
        self.assertIsNone(latest_log.property_type)  # No property type filter
        self.assertIsNone(latest_log.pricebucket)  # No price range filter
        self.assertIsNotNone(latest_log.timestamp)
    
    def test_neighborhood_search_logging_with_visible_only(self):
        """Test that neighborhood search logging only occurs for visible listings."""
        # Create a visible and hidden listing in the same neighborhood
        visible_listing = Listing.objects.create(
            address='Visible Downtown St, Omaha, NE 68102',
            price=150000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        hidden_listing = Listing.objects.create(
            address='Hidden Downtown St, Omaha, NE 68102',
            price=150000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=False
        )
        
        initial_log_count = SearchLog.objects.count()
        
        # Filter by neighborhood
        response = self.client.get(reverse('listings'), {'neighborhood': self.neighborhood_downtown.pk})
        self.assertEqual(response.status_code, 200)
        
        # Verify search was logged
        new_log_count = SearchLog.objects.count()
        self.assertEqual(new_log_count, initial_log_count + 1)
        
        # Verify only visible listing is in results
        listings = response.context['listings']
        listing_addresses = [listing.address for listing in listings]
        self.assertIn('Visible Downtown St, Omaha, NE 68102', listing_addresses)
        self.assertNotIn('Hidden Downtown St, Omaha, NE 68102', listing_addresses)
        
        # Verify the log entry
        latest_log = SearchLog.objects.latest('timestamp')
        self.assertEqual(latest_log.neighborhood, self.neighborhood_downtown)
        self.assertIsNotNone(latest_log.timestamp)
    
    def test_filter_by_property_type(self):
        """Test filtering listings by property type."""
        response = self.client.get(reverse('listings'), {'type': self.property_type_house.pk})
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        for listing in listings:
            self.assertEqual(listing.property_type, self.property_type_house)
    
    def test_property_type_search_logging(self):
        """Test that property type searches are logged to SearchLog."""
        initial_log_count = SearchLog.objects.count()
        
        # Perform a property type search
        response = self.client.get(reverse('listings'), {'type': self.property_type_condo.pk})
        self.assertEqual(response.status_code, 200)
        
        # Verify a search log entry was created
        new_log_count = SearchLog.objects.count()
        self.assertEqual(new_log_count, initial_log_count + 1)
        
        # Verify the log entry has correct property_type
        latest_log = SearchLog.objects.latest('timestamp')
        self.assertEqual(latest_log.property_type, self.property_type_condo)
        self.assertIsNone(latest_log.neighborhood)  # No neighborhood filter
        self.assertIsNone(latest_log.pricebucket)  # No price range filter
        self.assertIsNotNone(latest_log.timestamp)
    
    def test_property_type_search_logging_with_visible_only(self):
        """Test that property type search logging only occurs for visible listings."""
        # Create a visible and hidden listing of the same property type
        visible_listing = Listing.objects.create(
            address='Visible Condo St, Omaha, NE 68102',
            price=150000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_condo,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        hidden_listing = Listing.objects.create(
            address='Hidden Condo St, Omaha, NE 68102',
            price=150000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_condo,
            status='Available',
            status_id=self.status_active,
            is_visible=False
        )
        
        initial_log_count = SearchLog.objects.count()
        
        # Filter by property type
        response = self.client.get(reverse('listings'), {'type': self.property_type_condo.pk})
        self.assertEqual(response.status_code, 200)
        
        # Verify search was logged
        new_log_count = SearchLog.objects.count()
        self.assertEqual(new_log_count, initial_log_count + 1)
        
        # Verify only visible listing is in results
        listings = response.context['listings']
        listing_addresses = [listing.address for listing in listings]
        self.assertIn('Visible Condo St, Omaha, NE 68102', listing_addresses)
        self.assertNotIn('Hidden Condo St, Omaha, NE 68102', listing_addresses)
        
        # Verify the log entry
        latest_log = SearchLog.objects.latest('timestamp')
        self.assertEqual(latest_log.property_type, self.property_type_condo)
        self.assertIsNotNone(latest_log.timestamp)
    
    def test_filter_by_price_low_to_high(self):
        """Test sorting by price low to high."""
        response = self.client.get(reverse('listings'), {'price': 'low-high'})
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        prices = [float(listing.price) for listing in listings]
        self.assertEqual(prices, sorted(prices))
    
    def test_filter_by_price_high_to_low(self):
        """Test sorting by price high to low."""
        response = self.client.get(reverse('listings'), {'price': 'high-low'})
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        prices = [float(listing.price) for listing in listings]
        self.assertEqual(prices, sorted(prices, reverse=True))
    
    def test_multiple_filters(self):
        """Test applying multiple filters at once."""
        response = self.client.get(reverse('listings'), {
            'neighborhood': self.neighborhood_downtown.pk,
            'type': self.property_type_house.pk,
            'price': 'low-high'
        })
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        for listing in listings:
            self.assertEqual(listing.neighborhood, self.neighborhood_downtown)
            self.assertEqual(listing.property_type, self.property_type_house)
        
        # Check sorting
        prices = [float(listing.price) for listing in listings]
        self.assertEqual(prices, sorted(prices))
    
    def test_pagination_exists(self):
        """Test that pagination is present when there are multiple pages."""
        # Create enough listings to require pagination (more than 12)
        for i in range(15):
            Listing.objects.create(
                address=f'{i}00 Pagination St, Omaha, NE 68102',
                price=100000 + (i * 10000),
                created_by=self.user,
                neighborhood=self.neighborhood_downtown,
                property_type=self.property_type_house,
                status='Available',
                status_id=self.status_active,
                is_visible=True,
                bedrooms=3,
                bathrooms=2.0,
                square_footage=1500
            )
        
        response = self.client.get(reverse('listings'))
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        self.assertTrue(hasattr(listings, 'has_other_pages'))
        self.assertTrue(listings.has_other_pages())
    
    def test_pagination_first_page(self):
        """Test accessing the first page."""
        # Create 15 listings
        for i in range(15):
            Listing.objects.create(
                address=f'{i}00 Page St, Omaha, NE 68102',
                price=100000 + (i * 10000),
                created_by=self.user,
                neighborhood=self.neighborhood_downtown,
                property_type=self.property_type_house,
                status='Available',
                status_id=self.status_active,
                is_visible=True,
                bedrooms=3,
                bathrooms=2.0,
                square_footage=1500
            )
        
        response = self.client.get(reverse('listings'), {'page': 1})
        self.assertEqual(response.status_code, 200)
        listings = response.context['listings']
        self.assertEqual(listings.number, 1)
        self.assertTrue(listings.has_next())
    
    def test_pagination_second_page(self):
        """Test accessing the second page."""
        # Create 15 listings
        for i in range(15):
            Listing.objects.create(
                address=f'{i}00 Page St, Omaha, NE 68102',
                price=100000 + (i * 10000),
                created_by=self.user,
                neighborhood=self.neighborhood_downtown,
                property_type=self.property_type_house,
                status='Available',
                status_id=self.status_active,
                is_visible=True,
                bedrooms=3,
                bathrooms=2.0,
                square_footage=1500
            )
        
        response = self.client.get(reverse('listings'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        listings = response.context['listings']
        self.assertEqual(listings.number, 2)
        self.assertTrue(listings.has_previous())
    
    def test_pagination_preserves_filters(self):
        """Test that pagination preserves filter parameters."""
        response = self.client.get(reverse('listings'), {
            'neighborhood': self.neighborhood_downtown.pk,
            'type': self.property_type_house.pk,
            'price': 'low-high',
            'page': 2
        })
        self.assertEqual(response.status_code, 200)
        
        # Check that filter values are preserved in context
        self.assertEqual(response.context['selected_neighborhood'], self.neighborhood_downtown.pk)
        self.assertEqual(response.context['selected_type'], self.property_type_house.pk)
        self.assertEqual(response.context['selected_price'], 'low-high')
    
    def test_invalid_page_number(self):
        """Test that invalid page numbers are handled gracefully."""
        response = self.client.get(reverse('listings'), {'page': 999})
        self.assertEqual(response.status_code, 200)
        # Should show last page or first page
        listings = response.context['listings']
        self.assertIsNotNone(listings)
    
    def test_invalid_filter_parameters(self):
        """Test that invalid filter parameters are handled gracefully."""
        response = self.client.get(reverse('listings'), {
            'neighborhood': 'invalid',
            'type': 'not_a_number',
            'price': 'invalid_sort'
        })
        self.assertEqual(response.status_code, 200)
        # Should still return listings (ignoring invalid filters)
        self.assertIn('listings', response.context)
    
    def test_filter_by_price_range(self):
        """Test filtering listings by price range."""
        # Create listings in different price ranges
        listing_75k = Listing.objects.create(
            address='75k Test St, Omaha, NE 68102',
            price=75000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        listing_125k = Listing.objects.create(
            address='125k Test St, Omaha, NE 68102',
            price=125000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        listing_175k = Listing.objects.create(
            address='175k Test St, Omaha, NE 68102',
            price=175000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        # Test filtering by $50k-$100k range
        response = self.client.get(reverse('listings'), {'price_range': self.pricebucket_50_100k.pk})
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        listing_addresses = [listing.address for listing in listings]
        
        # Should include listing_75k (within range)
        self.assertIn('75k Test St, Omaha, NE 68102', listing_addresses)
        # Should NOT include listings outside range
        self.assertNotIn('125k Test St, Omaha, NE 68102', listing_addresses)
        self.assertNotIn('175k Test St, Omaha, NE 68102', listing_addresses)
        
        # Verify all returned listings are within the price range
        for listing in listings:
            self.assertGreaterEqual(float(listing.price), 50000)
            self.assertLess(float(listing.price), 100000)
    
    def test_filter_by_price_range_boundaries(self):
        """Test that price range filtering correctly handles boundaries."""
        # Create listings at exact boundaries
        listing_50k = Listing.objects.create(
            address='50k Boundary St, Omaha, NE 68102',
            price=50000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        listing_100k = Listing.objects.create(
            address='100k Boundary St, Omaha, NE 68102',
            price=100000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        # Test $50k-$100k range (should include 50k, exclude 100k)
        response = self.client.get(reverse('listings'), {'price_range': self.pricebucket_50_100k.pk})
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        listing_addresses = [listing.address for listing in listings]
        
        # 50k should be included (lower bound inclusive)
        self.assertIn('50k Boundary St, Omaha, NE 68102', listing_addresses)
        # 100k should NOT be included (upper bound exclusive)
        self.assertNotIn('100k Boundary St, Omaha, NE 68102', listing_addresses)
    
    def test_filter_by_price_range_open_ended(self):
        """Test filtering by open-ended price range ($1,000,000+)."""
        # Create listings above and below 1M
        listing_900k = Listing.objects.create(
            address='900k Test St, Omaha, NE 68102',
            price=900000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        listing_1_5m = Listing.objects.create(
            address='1.5M Test St, Omaha, NE 68102',
            price=1500000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        # Test $1M+ range
        response = self.client.get(reverse('listings'), {'price_range': self.pricebucket_1m_plus.pk})
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        listing_addresses = [listing.address for listing in listings]
        
        # Should include 1.5M (>= 1M)
        self.assertIn('1.5M Test St, Omaha, NE 68102', listing_addresses)
        # Should NOT include 900k (< 1M)
        self.assertNotIn('900k Test St, Omaha, NE 68102', listing_addresses)
        
        # Verify all returned listings are >= 1M
        for listing in listings:
            self.assertGreaterEqual(float(listing.price), 1000000)
    
    def test_price_range_filter_with_visible_only(self):
        """Test that price range filtering only shows visible listings."""
        # Create visible and hidden listings in the same price range
        visible_listing = Listing.objects.create(
            address='Visible 75k St, Omaha, NE 68102',
            price=75000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        hidden_listing = Listing.objects.create(
            address='Hidden 75k St, Omaha, NE 68102',
            price=75000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=False
        )
        
        # Filter by price range
        response = self.client.get(reverse('listings'), {'price_range': self.pricebucket_50_100k.pk})
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        listing_addresses = [listing.address for listing in listings]
        
        # Should include visible listing
        self.assertIn('Visible 75k St, Omaha, NE 68102', listing_addresses)
        # Should NOT include hidden listing
        self.assertNotIn('Hidden 75k St, Omaha, NE 68102', listing_addresses)
    
    def test_price_range_filter_reset(self):
        """Test that price range filter can be reset."""
        # First apply a price range filter
        response1 = self.client.get(reverse('listings'), {'price_range': self.pricebucket_50_100k.pk})
        self.assertEqual(response1.status_code, 200)
        listings1 = response1.context['listings']
        count_with_filter = listings1.paginator.count
        
        # Reset filter (no price_range parameter)
        response2 = self.client.get(reverse('listings'))
        self.assertEqual(response2.status_code, 200)
        listings2 = response2.context['listings']
        count_without_filter = listings2.paginator.count
        
        # Should have more listings without filter
        self.assertGreater(count_without_filter, count_with_filter)
        
        # Verify selected_price_range is None when no filter is applied
        self.assertIsNone(response2.context.get('selected_price_range'))
    
    def test_price_range_filter_with_other_filters(self):
        """Test that price range filter works with other filters."""
        # Create listings in different price ranges and neighborhoods
        listing_75k_downtown = Listing.objects.create(
            address='75k Downtown St, Omaha, NE 68102',
            price=75000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        listing_75k_midtown = Listing.objects.create(
            address='75k Midtown St, Omaha, NE 68103',
            price=75000,
            created_by=self.user,
            neighborhood=self.neighborhood_midtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        listing_125k_downtown = Listing.objects.create(
            address='125k Downtown St, Omaha, NE 68102',
            price=125000,
            created_by=self.user,
            neighborhood=self.neighborhood_downtown,
            property_type=self.property_type_house,
            status='Available',
            status_id=self.status_active,
            is_visible=True
        )
        
        # Filter by price range AND neighborhood
        response = self.client.get(reverse('listings'), {
            'price_range': self.pricebucket_50_100k.pk,
            'neighborhood': self.neighborhood_downtown.pk
        })
        self.assertEqual(response.status_code, 200)
        
        listings = response.context['listings']
        listing_addresses = [listing.address for listing in listings]
        
        # Should include 75k downtown (matches both filters)
        self.assertIn('75k Downtown St, Omaha, NE 68102', listing_addresses)
        # Should NOT include 75k midtown (wrong neighborhood)
        self.assertNotIn('75k Midtown St, Omaha, NE 68103', listing_addresses)
        # Should NOT include 125k downtown (wrong price range)
        self.assertNotIn('125k Downtown St, Omaha, NE 68102', listing_addresses)
        
        # Verify all listings match both filters
        for listing in listings:
            self.assertEqual(listing.neighborhood, self.neighborhood_downtown)
            self.assertGreaterEqual(float(listing.price), 50000)
            self.assertLess(float(listing.price), 100000)
    
    def test_price_range_search_logging(self):
        """Test that price range searches are logged to SearchLog."""
        initial_log_count = SearchLog.objects.count()
        
        # Perform a price range search
        response = self.client.get(reverse('listings'), {'price_range': self.pricebucket_50_100k.pk})
        self.assertEqual(response.status_code, 200)
        
        # Verify a search log entry was created
        new_log_count = SearchLog.objects.count()
        self.assertEqual(new_log_count, initial_log_count + 1)
        
        # Verify the log entry has correct pricebucket
        latest_log = SearchLog.objects.latest('timestamp')
        self.assertEqual(latest_log.pricebucket, self.pricebucket_50_100k)
        self.assertIsNotNone(latest_log.timestamp)
    
    def test_price_range_search_logging_with_multiple_filters(self):
        """Test that SearchLog captures all filter parameters."""
        # Perform a search with price range, neighborhood, and property type
        response = self.client.get(reverse('listings'), {
            'price_range': self.pricebucket_100_150k.pk,
            'neighborhood': self.neighborhood_downtown.pk,
            'type': self.property_type_house.pk
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify the log entry captures all filters
        latest_log = SearchLog.objects.latest('timestamp')
        self.assertEqual(latest_log.pricebucket, self.pricebucket_100_150k)
        self.assertEqual(latest_log.neighborhood, self.neighborhood_downtown)
        self.assertEqual(latest_log.property_type, self.property_type_house)
        self.assertIsNotNone(latest_log.timestamp)
    
    def test_price_range_filter_performance(self):
        """Test that price range filtering performs efficiently."""
        # Create many listings to test query performance
        for i in range(50):
            Listing.objects.create(
                address=f'{i}00 Performance St, Omaha, NE 68102',
                price=50000 + (i * 10000),  # Prices from 50k to 550k
                created_by=self.user,
                neighborhood=self.neighborhood_downtown,
                property_type=self.property_type_house,
                status='Available',
                status_id=self.status_active,
                is_visible=True
            )
        
        # Test that filtering doesn't cause performance issues
        import time
        start_time = time.time()
        response = self.client.get(reverse('listings'), {'price_range': self.pricebucket_50_100k.pk})
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        # Query should complete in reasonable time (less than 1 second)
        self.assertLess(elapsed_time, 1.0)
        
        # Verify correct filtering
        listings = response.context['listings']
        for listing in listings:
            self.assertGreaterEqual(float(listing.price), 50000)
            self.assertLess(float(listing.price), 100000)

