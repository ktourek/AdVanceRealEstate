# listings/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Listing, Photo
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
    """Page showing all available listings."""
    listings = Listing.objects.filter(is_visible=True).order_by('-listed_date')
    return render(request, 'listings/all_listings.html', {'listings': listings})


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
            listing.save()
            
            # Handle photos
            photos = request.FILES.getlist('photos')
            for i, photo_file in enumerate(photos):
                Photo.objects.create(
                    listing=listing,
                    image_data=photo_file.read(),
                    photo_display_order=i+1
                )
            
            return redirect('home')
    else:
        form = ListingForm()
    
    return render(request, 'listings/add_listing.html', {'form': form})


def custom_logout(request):
    """Custom logout view that renders the logout page."""
    logout(request)
    return render(request, 'accounts/logout.html')
