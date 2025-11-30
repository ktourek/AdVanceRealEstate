# listings/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_alias'),
    path('listings/', views.all_listings, name='listings'),
    path('omaha/', views.omaha, name='omaha'),
    path('add-listing/', views.add_listing, name='add_listing'),
    path('photo/<int:photo_id>/', views.listing_photo, name='listing_photo'),
    path('photo/<int:photo_id>/thumbnail/', views.listing_photo_thumbnail, name='listing_photo_thumbnail'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            authentication_form=CustomLoginForm
        ),
        name='login'
    ),
    path('logout/', views.custom_logout, name='logout'),
    
    # Omaha Management URLs
    path('omaha/manage/', views.manage_omaha, name='manage_omaha'),
    path('omaha/add/', views.add_omaha_location, name='add_omaha_location'),
    path('omaha/edit/<int:location_id>/', views.edit_omaha_location, name='edit_omaha_location'),
    path('omaha/delete/<int:location_id>/', views.delete_omaha_location, name='delete_omaha_location'),
    
    # Report Generation URLs
    path('report/', views.generate_report, name='generate_report'),
    path('report/export/', views.export_report_csv, name='export_report_csv'),
    
    # User registration removed - users are managed by admin in Django admin interface
]


