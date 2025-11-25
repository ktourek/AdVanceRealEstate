# listings/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Listing


class CustomLoginForm(AuthenticationForm):
    """Custom login form using email instead of username."""
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autofocus': True,
            'placeholder': 'E-mail'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class ListingForm(forms.ModelForm):
    """Form for creating new property listings."""
    photos = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True}),
        label='Upload Property Photos',
        help_text='Please upload exactly 4 images.'
    )

    class Meta:
        model = Listing
        fields = [
            'address', 'price', 'property_type', 'neighborhood',
            'bedrooms', 'bathrooms', 'square_footage', 'status', 'description'
        ]
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234 Elm St , Omaha, NE 12345'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '456000'}),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'neighborhood': forms.Select(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1'}),
            'square_footage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1500'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the property, features, and nearby attractions...'}),
        }
        labels = {
            'property_type': 'Home Type',
            'square_footage': "Home's Square Footage",
            'status': 'Listing Status',
        }

    def clean_photos(self):
        """Validate that exactly 4 photos are uploaded."""
        photos = self.files.getlist('photos')
        if len(photos) != 4:
            raise forms.ValidationError(f'You must upload exactly 4 photos. You uploaded {len(photos)}.')
        
        for photo in photos:
            if not photo.content_type.startswith('image/'):
                raise forms.ValidationError('File must be an image.')
            if photo.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Image file too large ( > 5MB )')
        return photos

