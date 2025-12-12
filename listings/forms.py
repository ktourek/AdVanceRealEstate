# listings/forms.py
from django import forms
from django import forms
from django.core.validators import validate_email
from django.contrib.auth.forms import AuthenticationForm
from django.template.base import logger
from .models import Listing, OmahaLocation, Photo


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
    photos = MultipleFileField(label='Upload Property Photos', required=False)

    class Meta:
        model = Listing
        fields = ['address', 'price', 'property_type', 'neighborhood',
                  'bedrooms', 'bathrooms', 'square_footage', 'description',
                  'status_id', 'photos']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'status_id': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'status_id': 'Listing Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status_id'].empty_label = None
        self.fields['status_id'].required = True
        
        # Add 'form-control' class to all form fields for consistent styling
        for field_name, field in self.fields.items():
            if field_name != 'photos':  # Skip photos field as it's handled separately
                existing_classes = field.widget.attrs.get('class', '')
                if 'form-control' not in existing_classes:
                    field.widget.attrs['class'] = (existing_classes + ' form-control').strip()

    def save_photos(self, listing):
            photos = self.cleaned_data.get('photos')
            if not photos:
                return

            for i, photo_file in enumerate(photos, start=1):
                try:
                    try:
                        photo_file.seek(0)
                    except Exception:
                        pass

                    if hasattr(Photo, 'image'):
                        p = Photo(listing=listing)
                        p.image.save(photo_file.name, photo_file, save=False)
                        p.photo_display_order = i
                        p.save()
                        continue

                    if hasattr(Photo, 'image_data'):
                        data = photo_file.read()
                        Photo.objects.create(listing=listing, image_data=data, photo_display_order=i)
                        continue

                    Photo.objects.create(listing=listing, photo=photo_file)
                except Exception:
                    logger.exception("Failed to save uploaded photo for listing %s", getattr(listing, 'pk', None))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            try:
                self.save_photos(instance)
            except Exception:
                logger.exception("Error saving photos for listing %s", getattr(instance, 'pk', None))
        return instance

    def clean_photos(self):
        photos = self.cleaned_data.get('photos')
        
        if not self.instance or not self.instance.pk:
            if not photos:
                raise forms.ValidationError('Please upload photos.')
            if len(photos) != 4:
                raise forms.ValidationError(f'You must upload exactly 4 photos. You uploaded {len(photos)}.')
            for photo in photos:
                if not photo.content_type.startswith('image/'):
                    raise forms.ValidationError('File must be an image.')
                if photo.size > 5 * 1024 * 1024:
                    raise forms.ValidationError('Image file too large ( > 5MB )')
            return photos
        else:
            return None

        #     """Form for creating new property listings."""
#     photos = MultipleFileField(
#         label='Upload Property Photos',
#         help_text='Please upload exactly 4 images.',
#         required=True
#     )

#     class Meta:
#         model = Listing
#         fields = [
#             'address', 'price', 'property_type', 'neighborhood',
#             'bedrooms', 'bathrooms', 'square_footage', 'status', 'description'
#         ]
#         widgets = {
#             'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address information'}),
#             'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
#             'property_type': forms.Select(attrs={'class': 'form-control'}),
#             'neighborhood': forms.Select(attrs={'class': 'form-control'}),
#             'bedrooms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter number of bedrooms'}),
#             'bathrooms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter number of bathrooms'}),
#             'square_footage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter square footage'}),
#             'status': forms.Select(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the property, features, and nearby attractions...'}),
#         }
#         labels = {
#             'property_type': 'Home Type',
#             'square_footage': "Home's Square Footage",
#             'status': 'Listing Status',
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Add empty_label for ForeignKey select fields with meaningful messages
#         self.fields['property_type'].empty_label = 'Select a home type'
#         self.fields['neighborhood'].empty_label = 'Select a neighborhood'

#         # For CharField with choices (status), add an empty choice at the beginning
#         self.fields['status'].choices = [('', 'Select listing status')] + list(self.fields['status'].choices)

#     def clean_photos(self):
#         """Validate that exactly 4 photos are uploaded."""
#         photos = self.cleaned_data.get('photos')

#         if not photos:
#             raise forms.ValidationError('Please upload photos.')

#         if len(photos) != 4:
#             raise forms.ValidationError(f'You must upload exactly 4 photos. You uploaded {len(photos)}.')

#         for photo in photos:
#             if not photo.content_type.startswith('image/'):
#                 raise forms.ValidationError('File must be an image.')
#             if photo.size > 5 * 1024 * 1024:  # 5MB limit
#                 raise forms.ValidationError('Image file too large ( > 5MB )')
#         return photos

class ListingStatusPriceForm(forms.ModelForm):
    """Form for secure management dashboard – Madison can only edit price and status."""
    class Meta:
        model = Listing
        fields = ['price', 'status_id']
        widgets = {
            'status_id': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'status_id': 'Listing Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Match ListingForm behaviour
        self.fields['status_id'].empty_label = None
        self.fields['status_id'].required = True

        # Add 'form-control' to both fields for consistent styling
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            if 'form-control' not in existing_classes:
                field.widget.attrs['class'] = (existing_classes + ' form-control').strip()

    def clean_price(self):
        """
        Numeric validation for price (required, > 0, allow '200,000' or '$200000').
        """
        from decimal import Decimal, InvalidOperation

        price = self.cleaned_data.get('price')

        if price in (None, ''):
            raise forms.ValidationError("Price is required.")

        # If user typed a string like "$200,000"
        if isinstance(price, str):
            cleaned = price.replace(',', '').replace('$', '').strip()
            try:
                price_val = Decimal(cleaned)
            except InvalidOperation:
                raise forms.ValidationError("Enter a valid numeric price.")
        else:
            price_val = price

        if price_val <= 0:
            raise forms.ValidationError("Price must be greater than zero.")

        return price_val

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


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your name',
            'autocomplete': 'name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your email',
            'autocomplete': 'email'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Your message...',
            'rows': 5
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label = False
            field.widget.attrs.update({'style': ''})


