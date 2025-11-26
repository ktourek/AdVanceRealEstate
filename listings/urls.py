# listings/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_alias'),
    path('listings/', views.all_listings, name='listings'),
    path('add-listing/', views.add_listing, name='add_listing'),
    path('photo/<int:photo_id>/', views.listing_photo, name='listing_photo'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            authentication_form=CustomLoginForm
        ),
        name='login'
    ),
    path('logout/', views.custom_logout, name='logout'),
    # User registration removed - users are managed by admin in Django admin interface
]
