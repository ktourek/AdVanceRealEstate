# listings/views.py
from django.shortcuts import render
from .models import Listing


def home(request):
    """Public homepage showing published listings."""
    # Use is_visible for filtering (backward compatible with is_published property)
    listings = Listing.objects.filter(is_visible=True).order_by('-listed_date')
    return render(request, 'listings/home.html', {'listings': listings})
