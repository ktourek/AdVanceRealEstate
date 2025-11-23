from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from .views import logout_view  

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home page at templates/home.html
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Login using templates/accounts/login.html
    path('accounts/login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),

    # logout view that accepts GET and POST and renders accounts/logout.html from realestate_portal/views.py
    path('accounts/logout/', logout_view, name='logout'),

    # Keep the rest of the built-in auth urls
    path('accounts/', include('django.contrib.auth.urls')),

    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),

]