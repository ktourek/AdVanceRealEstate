# listings/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Status, PropertyType, Neighborhood, Pricebucket,
    Listing, Photo, SearchLog, OmahaResource
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model."""
    list_display = ['email', 'firstname', 'lastname', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['email', 'firstname', 'lastname']
    ordering = ['email']
    readonly_fields = ['date_joined']  # Make date_joined read-only since it's auto-set
    
    # Remove filter_horizontal since we don't have groups/user_permissions
    filter_horizontal = []
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('firstname', 'lastname')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('date_joined',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstname', 'lastname', 'password1', 'password2'),
        }),
    )


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Pricebucket)
class PricebucketAdmin(admin.ModelAdmin):
    list_display = ['range']
    search_fields = ['range']


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = [
        'address', 'price', 'property_type', 'neighborhood',
        'status', 'is_visible', 'is_featured', 'created_by', 'listed_date'
    ]
    list_filter = [
        'property_type', 'neighborhood', 'status', 'is_visible',
        'is_featured', 'status_id', 'listed_date'
    ]
    search_fields = ['address', 'description']
    readonly_fields = ['listed_date']
    fieldsets = (
        ('Basic Information', {
            'fields': ('address', 'price', 'description', 'created_by')
        }),
        ('Property Details', {
            'fields': (
                'property_type', 'neighborhood', 'pricebucket',
                'bedrooms', 'bathrooms', 'square_footage'
            )
        }),
        ('Status & Visibility', {
            'fields': ('status', 'status_id', 'is_visible', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('listed_date',)
        }),
    )


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['photo_id', 'listing', 'photo_display_order']
    list_filter = ['listing']
    search_fields = ['listing__address']


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ['search_log_id', 'property_type', 'neighborhood', 'pricebucket', 'timestamp']
    list_filter = ['property_type', 'neighborhood', 'pricebucket', 'timestamp']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(OmahaResource)
class OmahaResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'user', 'url']
    list_filter = ['category', 'is_published', 'user']
    search_fields = ['title', 'description']
    fieldsets = (
        ('Resource Information', {
            'fields': ('title', 'description', 'category', 'url')
        }),
        ('Publication', {
            'fields': ('user', 'is_published')
        }),
    )
