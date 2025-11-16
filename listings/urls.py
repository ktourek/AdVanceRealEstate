# listings/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_alias'),  # allow /home/ as well
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            authentication_form=CustomLoginForm
        ),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # User registration removed - users are managed by admin in Django admin interface
]
