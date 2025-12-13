from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_alias'),
    path('about/', views.about, name='about'),
    path('featured/update/', views.update_featured_listing, name='featured_listing_update'),
    path('listings/', views.all_listings, name='listings'),
    path('listings/<int:listing_id>/', views.ListingDetailView.as_view(), name='listing_detail'),
    path('add-listing/', views.add_listing, name='add_listing'),
    path('listings/<int:listing_id>/edit/', views.edit_listing, name='edit_listing'),
    path('listings/<int:listing_id>/toggle-visibility/', views.toggle_listing_visibility, name='toggle_visibility'),
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

    path('omaha/', views.omaha, name='omaha'),
    path('omaha/manage/', views.manage_omaha, name='manage_omaha'),
    path('omaha/add/', views.add_omaha_location, name='add_omaha_location'),
    path('omaha/edit/<int:location_id>/', views.edit_omaha_location, name='edit_omaha_location'),
    path('omaha/delete/<int:location_id>/', views.delete_omaha_location, name='delete_omaha_location'),

    path('report/', views.generate_report, name='generate_report'),
    path('report/export/', views.export_report_csv, name='export_report_csv'),
]
