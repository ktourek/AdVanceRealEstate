from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Listing

def home(request):
    listings = Listing.objects.filter(is_published=True).order_by('-listed_date')
    return render(request, 'listings/home.html', {'listings': listings})
