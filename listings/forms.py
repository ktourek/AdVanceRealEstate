# listings/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomLoginForm(AuthenticationForm):
    """Custom login form using email instead of username."""
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autofocus': True,
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update field labels
        self.fields['username'].label = 'Email'
    
    def clean_username(self):
        """Normalize email to lowercase."""
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower().strip()
        return username

