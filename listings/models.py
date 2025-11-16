# listings/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    """Manager for custom User model."""
    
    def create_user(self, email, password=None, firstname='', lastname=''):
        """Create and return a regular user."""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            firstname=firstname,
            lastname=lastname
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, firstname='', lastname=''):
        """Create and return a superuser."""
        user = self.create_user(email, password, firstname, lastname)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Custom User model matching the database schema."""
    user_id = models.AutoField(primary_key=True, db_column='User_ID')
    email = models.EmailField(unique=True, db_column='Email')
    # Map Django's password field to Password_Hash column
    password = models.CharField(max_length=128, db_column='Password_Hash')
    firstname = models.CharField(max_length=100, db_column='Firstname')
    lastname = models.CharField(max_length=100, db_column='Lastname')
    
    # Django auth fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']
    
    class Meta:
        db_table = 'User'
        verbose_name = 'user'
        verbose_name_plural = 'users'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.firstname} {self.lastname}".strip()
    
    def get_short_name(self):
        return self.firstname
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser


class Status(models.Model):
    """Status lookup table."""
    status_id = models.AutoField(primary_key=True, db_column='Status_ID')
    name = models.CharField(max_length=100, db_column='Name')
    
    class Meta:
        db_table = 'Status'
        verbose_name_plural = 'Statuses'
    
    def __str__(self):
        return self.name


class PropertyType(models.Model):
    """Property Type lookup table."""
    property_type_id = models.AutoField(primary_key=True, db_column='Property_Type_ID')
    name = models.CharField(max_length=100, db_column='Name')
    
    class Meta:
        db_table = 'Property_Type'
        verbose_name = 'Property Type'
        verbose_name_plural = 'Property Types'
    
    def __str__(self):
        return self.name


class Neighborhood(models.Model):
    """Neighborhood lookup table."""
    neighborhood_id = models.AutoField(primary_key=True, db_column='Neighborhood_ID')
    name = models.CharField(max_length=100, db_column='Name')
    
    class Meta:
        db_table = 'Neighborhood'
    
    def __str__(self):
        return self.name


class Pricebucket(models.Model):
    """Price bucket lookup table."""
    pricebucket_id = models.AutoField(primary_key=True, db_column='Pricebucket_ID')
    range = models.CharField(max_length=100, db_column='Range')
    
    class Meta:
        db_table = 'Pricebucket'
    
    def __str__(self):
        return self.range


class Listing(models.Model):
    """Listing model matching the database schema."""
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Pending', 'Pending'),
        ('Sold', 'Sold'),
    ]
    
    listing_id = models.AutoField(primary_key=True, db_column='Listing_ID')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='Created_by',
        related_name='listings'
    )
    property_type = models.ForeignKey(
        PropertyType,
        on_delete=models.CASCADE,
        db_column='Property_Type_ID',
        related_name='listings'
    )
    neighborhood = models.ForeignKey(
        Neighborhood,
        on_delete=models.CASCADE,
        db_column='Neighborhood_ID',
        related_name='listings'
    )
    pricebucket = models.ForeignKey(
        Pricebucket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='Pricebucket_ID',
        related_name='listings'
    )
    address = models.CharField(max_length=255, db_column='Address')
    price = models.DecimalField(max_digits=12, decimal_places=2, db_column='Price')
    description = models.TextField(blank=True, null=True, db_column='Description')
    status_id = models.ForeignKey(
        Status,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='Status_ID',
        related_name='listings'
    )
    is_visible = models.BooleanField(default=True, db_column='Is_Visible')
    is_featured = models.BooleanField(default=False, db_column='Is_Featured')
    bedrooms = models.IntegerField(null=True, blank=True, db_column='Bedrooms')
    bathrooms = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        db_column='Bathrooms'
    )
    square_footage = models.IntegerField(null=True, blank=True, db_column='Square_Footage')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=True,
        blank=True,
        db_column='Status'
    )
    listed_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Listing'
        ordering = ['-listed_date']
    
    def __str__(self):
        return f"{self.address} - ${self.price}"
    
    # Keep compatibility with existing code
    @property
    def title(self):
        """Return address as title for backward compatibility."""
        return self.address
    
    @property
    def is_published(self):
        """Return is_visible as is_published for backward compatibility."""
        return self.is_visible


class Photo(models.Model):
    """Photo model for listing images."""
    photo_id = models.AutoField(primary_key=True, db_column='Photo_ID')
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        db_column='Listing_ID',
        related_name='photos'
    )
    image_data = models.BinaryField(null=True, blank=True, db_column='Image_Data')
    photo_display_order = models.IntegerField(
        null=True,
        blank=True,
        db_column='Photo_Display_Order'
    )
    
    class Meta:
        db_table = 'Photo'
        ordering = ['photo_display_order', 'photo_id']
    
    def __str__(self):
        return f"Photo {self.photo_id} for {self.listing.address}"


class SearchLog(models.Model):
    """Search log model for tracking searches."""
    search_log_id = models.AutoField(primary_key=True, db_column='Search_Log_ID')
    property_type = models.ForeignKey(
        PropertyType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='Property_Type_ID',
        related_name='search_logs'
    )
    neighborhood = models.ForeignKey(
        Neighborhood,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='Neighborhood_ID',
        related_name='search_logs'
    )
    pricebucket = models.ForeignKey(
        Pricebucket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='Pricebucket_ID',
        related_name='search_logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_column='Timestamp')
    
    class Meta:
        db_table = 'Search_Log'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Search log {self.search_log_id} - {self.timestamp}"


class OmahaResource(models.Model):
    """Omaha Resource model for optional resources page."""
    omaha_resource_id = models.AutoField(primary_key=True, db_column='Omaha_Resource_ID')
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='User_ID',
        related_name='omaha_resources'
    )
    title = models.CharField(max_length=200, db_column='Title')
    description = models.TextField(blank=True, null=True, db_column='Description')
    url = models.URLField(blank=True, null=True, db_column='URL')
    category = models.CharField(max_length=100, blank=True, null=True, db_column='Category')
    is_published = models.BooleanField(default=False, db_column='Is_Published')
    
    class Meta:
        db_table = 'Omaha_Resource'
    
    def __str__(self):
        return self.title
