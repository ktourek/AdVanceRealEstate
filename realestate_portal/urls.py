from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include listings app URLs (includes custom login/logout)
    path('', include('listings.urls')),

    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),

]