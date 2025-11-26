# listings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Listing, Photo, Neighborhood, PropertyType, Status
from .forms import ListingForm


@login_required
def home(request):
    """Public homepage showing featured listing and welcome message."""
    # Get the featured listing
    featured_listing = Listing.objects.filter(is_visible=True, is_featured=True).first()
    
    context = {
        'featured_listing': featured_listing,
    }
    return render(request, 'listings/home.html', context)


def all_listings(request):
    """Page showing all available listings with filtering and pagination."""
    # Start with all visible listings
    listings = Listing.objects.filter(is_visible=True).prefetch_related('photos').select_related('status_id', 'neighborhood', 'property_type')
    
    # Apply filters from query parameters
    neighborhood_id = request.GET.get('neighborhood', '').strip()
    property_type_id = request.GET.get('type', '').strip()
    price_sort = request.GET.get('price', '').strip()
    
    if neighborhood_id:
        try:
            neighborhood_id_int = int(neighborhood_id)
            # Use the database column name directly since db_column is custom
            listings = listings.filter(neighborhood_id=neighborhood_id_int)
        except (ValueError, TypeError):
            pass
    
    if property_type_id:
        try:
            property_type_id_int = int(property_type_id)
            # Use the database column name directly since db_column is custom
            listings = listings.filter(property_type_id=property_type_id_int)
        except (ValueError, TypeError):
            pass
    
    # Apply sorting
    if price_sort == 'low-high':
        listings = listings.order_by('price')
    elif price_sort == 'high-low':
        listings = listings.order_by('-price')
    else:
        listings = listings.order_by('-listed_date')
    
    # Pagination
    paginator = Paginator(listings, 12)  # Show 12 listings per page
    page = request.GET.get('page')
    
    try:
        paginated_listings = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        paginated_listings = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        paginated_listings = paginator.page(paginator.num_pages)
    
    neighborhoods = Neighborhood.objects.all().order_by('name')
    property_types = PropertyType.objects.all().order_by('name')
    
    # Preserve filter values in context for template (with error handling)
    try:
        selected_neighborhood = int(neighborhood_id) if neighborhood_id else None
    except (ValueError, TypeError):
        selected_neighborhood = None
    
    try:
        selected_type = int(property_type_id) if property_type_id else None
    except (ValueError, TypeError):
        selected_type = None
    
    context = {
        'listings': paginated_listings,
        'neighborhoods': neighborhoods,
        'property_types': property_types,
        'selected_neighborhood': selected_neighborhood,
        'selected_type': selected_type,
        'selected_price': price_sort or '',
    }
    
    return render(request, 'listings/all_listings.html', context)


@login_required
def add_listing(request):
    """View to add a new property listing."""
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            # Set is_visible based on status if needed, or default to True
            listing.is_visible = True 
            
            # Map status string to status_id ForeignKey
            status_value = form.cleaned_data.get('status')
            if status_value:
                status_mapping = {
                    'Available': 'Active',
                    'Pending': 'Pending',
                    'Sold': 'Sold'
                }
                status_name = status_mapping.get(status_value)
                if status_name:
                    try:
                        status_obj = Status.objects.get(name=status_name)
                        listing.status_id = status_obj
                    except Status.DoesNotExist:
                        pass  # Keep status_id as None if status not found
            
            listing.save()
            
            # Handle photos
            photos = request.FILES.getlist('photos')
            for i, photo_file in enumerate(photos):
                Photo.objects.create(
                    listing=listing,
                    image_data=photo_file.read(),
                    photo_display_order=i+1
                )
            
            return redirect('listings')
    else:
        form = ListingForm()
    
    return render(request, 'listings/add_listing.html', {'form': form})


def custom_logout(request):
    """Custom logout view that renders the logout page."""
    logout(request)
    return render(request, 'accounts/logout.html')


def listing_photo(request, photo_id):
    """View to serve listing photos from binary data."""
    photo = get_object_or_404(Photo, pk=photo_id)
    if photo.image_data:
        # Check image header to determine type
        image_header = photo.image_data[:8]
        if image_header.startswith(b'\x89PNG\r\n\x1a\n'):
            content_type = 'image/png'
        elif image_header.startswith(b'\xff\xd8\xff'):
            content_type = 'image/jpeg'
        elif image_header.startswith(b'GIF'):
            content_type = 'image/gif'
        else:
            # Default to PNG if unknown
            content_type = 'image/png'
        
        response = HttpResponse(photo.image_data, content_type=content_type)
        response['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
        return response
    return HttpResponse(status=404)
