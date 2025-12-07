# listings/forms.py
from django import forms
from django import forms
from django.core.validators import validate_email
from django.contrib.auth.forms import AuthenticationForm
from .models import Listing, OmahaLocation


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
    
    def value_from_datadict(self, data, files, name):
        """Handle multiple file uploads."""
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)


class MultipleFileField(forms.FileField):
    """Custom field to handle multiple file uploads."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """Clean and validate multiple files."""
        # Handle single file or list of files
        if isinstance(data, list):
            # If it's a list, return it as-is for further validation
            return data
        else:
            # If it's a single file, wrap it in a list
            single_file_clean = super().clean(data, initial)
            if single_file_clean is None:
                return None
            return [single_file_clean]

class FeaturedListingForm(forms.Form):
    listing = forms.ModelChoiceField(
        queryset=Listing.objects.filter(is_visible=True),
        required=False,
        label='Choose a Property',
        empty_label='Select a property',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['listing'].queryset = (
            Listing.objects
            .filter(is_visible=True)
            .exclude(status__iexact='Sold')
            .order_by('address')
        )
class ListingForm(forms.ModelForm):
    """Form for creating new property listings."""
    photos = MultipleFileField(
        label='Upload Property Photos',
        help_text='Please upload exactly 4 images.',
        required=True
    )

    class Meta:
        model = Listing
        fields = [
            'address', 'price', 'property_type', 'neighborhood',
            'bedrooms', 'bathrooms', 'square_footage', 'status', 'description'
        ]
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address information'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'neighborhood': forms.Select(attrs={'class': 'form-control'}),
            'bedrooms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter number of bedrooms'}),
            'bathrooms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter number of bathrooms'}),
            'square_footage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter square footage'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the property, features, and nearby attractions...'}),
        }
        labels = {
            'property_type': 'Home Type',
            'square_footage': "Home's Square Footage",
            'status': 'Listing Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty_label for ForeignKey select fields with meaningful messages
        self.fields['property_type'].empty_label = 'Select a home type'
        self.fields['neighborhood'].empty_label = 'Select a neighborhood'
        
        # For CharField with choices (status), add an empty choice at the beginning
        self.fields['status'].choices = [('', 'Select listing status')] + list(self.fields['status'].choices)

    def clean_photos(self):
        """Validate that exactly 4 photos are uploaded."""
        photos = self.cleaned_data.get('photos')
        
        if not photos:
            raise forms.ValidationError('Please upload photos.')
            
        if len(photos) != 4:
            raise forms.ValidationError(f'You must upload exactly 4 photos. You uploaded {len(photos)}.')
        
        for photo in photos:
            if not photo.content_type.startswith('image/'):
                raise forms.ValidationError('File must be an image.')
            if photo.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Image file too large ( > 5MB )')
        return photos


class OmahaLocationForm(forms.ModelForm):
    """Form for adding and editing Omaha locations."""
    class Meta:
        model = OmahaLocation
        fields = ['name', 'category', 'description', 'url', 'is_published', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Add a description of the location.'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Location Name',
            'url': 'Location URL',
            'is_published': 'Publish immediately',
        }
        help_texts = {
            'display_order': 'Lower numbers appear first within the category.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Select a Category'
