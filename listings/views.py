from django.shortcuts import render
from .models import Listing

def home(request):
    """Public homepage showing published listings."""
    listings = Listing.objects.filter(is_published=True).order_by('-listed_date')
    return render(request, 'listings/home.html', {'listings': listings})