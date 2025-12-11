# listings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.template.loader import render_to_string
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from decimal import Decimal
import logging
import re
from .forms import ContactForm
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.core.mail import BadHeaderError, send_mail
from .forms import ListingForm
from .models import Listing

from .models import (
    Listing, Photo, Neighborhood, PropertyType,
    Status, Pricebucket, SearchLog, OmahaLocation
)
from .forms import ListingForm, OmahaLocationForm

logger = logging.getLogger(__name__)


def home(request):
    """Public homepage showing featured listing and welcome message."""
    featured_listing = Listing.objects.filter(is_visible=True, is_featured=True).first()

    is_featured_sold = False
    if request.user.is_authenticated and featured_listing:
        status_str = str(getattr(featured_listing, 'status', '') or '')
        is_featured_sold = status_str == 'Sold'

    context = {
        'featured_listing': featured_listing,
        'is_featured_sold': is_featured_sold,
    }
    return render(request, 'listings/home.html', context)


@login_required
def update_featured_listing(request):
    """
    Simple admin endpoint to set a listing as featured.
    Uses a plain listing_id POST param to avoid requiring a custom form class.
    GET renders a simple selector template with available listings.
    """
    current_featured = Listing.objects.filter(is_featured=True).first()

    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        # Clear all featured flags
        Listing.objects.update(is_featured=False)

        if listing_id:
            try:
                new_featured = Listing.objects.get(pk=int(listing_id))
                new_featured.is_featured = True
                new_featured.save(update_fields=["is_featured"])
            except (Listing.DoesNotExist, ValueError):
                messages.error(request, "Selected listing not found.")
            else:
                messages.success(request, "Featured property updated.")
        else:
            messages.success(request, "Featured property cleared.")

        return redirect("home")

    listings = Listing.objects.order_by('-listed_date')[:200]
    is_sold = False
    if current_featured and str(current_featured.status) == 'Sold':
        is_sold = True

    context = {
        "current_featured": current_featured,
        "is_sold": is_sold,
        "listings": listings,
    }
    return render(request, "listings/update_featured_listing.html", context)


def all_listings(request):
    """Page showing all available listings with filtering and pagination."""
    ajax_param = request.GET.get('ajax', '')
    is_ajax = ajax_param == '1' or ajax_param == 'true'

    if not is_ajax:
        if hasattr(request, 'headers'):
            header_val = request.headers.get('X-Requested-With', '')
            is_ajax = header_val == 'XMLHttpRequest'
        if not is_ajax and 'HTTP_X_REQUESTED_WITH' in request.META:
            is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    listings = Listing.objects.prefetch_related('photos').select_related('status_id', 'neighborhood', 'property_type')

    neighborhood_id = request.GET.get('neighborhood', '').strip()
    property_type_id = request.GET.get('type', '').strip()
    price_sort = request.GET.get('price', '').strip()
    price_range_id = request.GET.get('price_range', '').strip()
    visibility = request.GET.get('visibility', '').strip()

    should_log_search = False
    search_log_pricebucket = None
    search_log_neighborhood = None
    search_log_property_type = None

    if neighborhood_id:
        try:
            neighborhood_id_int = int(neighborhood_id)
            listings = listings.filter(neighborhood_id=neighborhood_id_int)
            search_log_neighborhood = Neighborhood.objects.filter(pk=neighborhood_id_int).first()
            should_log_search = True
        except (ValueError, TypeError):
            pass

    if property_type_id:
        try:
            property_type_id_int = int(property_type_id)
            listings = listings.filter(property_type_id=property_type_id_int)
            search_log_property_type = PropertyType.objects.filter(pk=property_type_id_int).first()
            should_log_search = True
        except (ValueError, TypeError):
            pass

    if price_range_id:
        try:
            price_range_id_int = int(price_range_id)
            pricebucket = Pricebucket.objects.filter(pk=price_range_id_int).first()
            if pricebucket:
                range_str = pricebucket.range
                min_price, max_price = parse_price_range(range_str)

                if min_price is not None:
                    if max_price is not None:
                        listings = listings.filter(price__gte=min_price, price__lt=max_price)
                    else:
                        listings = listings.filter(price__gte=min_price)

                search_log_pricebucket = pricebucket
                should_log_search = True
        except (ValueError, TypeError):
            pass

    if price_sort == 'low-high':
        listings = listings.order_by('price')
    elif price_sort == 'high-low':
        listings = listings.order_by('-price')
    else:
        listings = listings.order_by('-listed_date')

    # visibility filter for authenticated users (optional)
    # visibility filter
    if request.user.is_authenticated:
        if visibility == 'hidden':
            listings = listings.filter(is_visible=False)
        elif visibility == 'all':
            pass
        else:
            listings = listings.filter(is_visible=True)
    else:
        listings = listings.filter(is_visible=True)

    if should_log_search:
        SearchLog.objects.create(
            pricebucket=search_log_pricebucket,
            neighborhood=search_log_neighborhood,
            property_type=search_log_property_type,
            timestamp=timezone.now()
        )

    paginator = Paginator(listings, 12)
    page = request.GET.get('page')

    try:
        paginated_listings = paginator.page(page)
    except PageNotAnInteger:
        paginated_listings = paginator.page(1)
    except EmptyPage:
        paginated_listings = paginator.page(paginator.num_pages)

    neighborhoods = Neighborhood.objects.all().order_by('name')
    property_types = PropertyType.objects.all().order_by('name')
    pricebuckets = Pricebucket.objects.all().order_by('pricebucket_id')

    try:
        selected_neighborhood = int(neighborhood_id) if neighborhood_id else None
    except (ValueError, TypeError):
        selected_neighborhood = None

    try:
        selected_type = int(property_type_id) if property_type_id else None
    except (ValueError, TypeError):
        selected_type = None

    try:
        selected_price_range = int(price_range_id) if price_range_id else None
    except (ValueError, TypeError):
        selected_price_range = None

    context = {
        'listings': paginated_listings,
        'neighborhoods': neighborhoods,
        'property_types': property_types,
        'pricebuckets': pricebuckets,
        'selected_neighborhood': selected_neighborhood,
        'selected_type': selected_type,
        'selected_price': price_sort or '',
        'selected_price_range': selected_price_range,
        'selected_visibility': visibility or '',
    }

    if is_ajax:
        try:
            listings_html = render_to_string('listings/listing_fragment.html', {'listings': paginated_listings}, request=request)
            pagination_html = render_to_string('listings/pagination_fragment.html', {
                'listings': paginated_listings,
                'selected_price': price_sort or '',
                'selected_price_range': selected_price_range,
                'selected_neighborhood': selected_neighborhood,
                'selected_type': selected_type,
                'selected_visibility': visibility or '',
            }, request=request)

            response = JsonResponse({
                'listings_html': listings_html,
                'pagination_html': pagination_html,
                'has_listings': paginated_listings.paginator.count > 0,
                'total_count': paginated_listings.paginator.count,
                'current_page': paginated_listings.number,
                'total_pages': paginated_listings.paginator.num_pages,
            })
            response['Content-Type'] = 'application/json'
            return response
        except Exception as e:
            import traceback
            error_response = JsonResponse({
                'error': str(e),
                'traceback': traceback.format_exc(),
                'listings_html': '<div class="no-listings"><p>Error loading listings.</p></div>',
                'pagination_html': '',
            }, status=500)
            error_response['Content-Type'] = 'application/json'
            return error_response

    return render(request, 'listings/all_listings.html', context)


def parse_price_range(range_str):
    """
    Parse a price range string and return (min_price, max_price) tuple.
    """
    try:
        range_str = range_str.replace('$', '').replace(',', '').strip()

        if '+' in range_str:
            min_price = Decimal(range_str.replace('+', '').strip())
            return (min_price, None)

        if ' - ' in range_str:
            parts = range_str.split(' - ')
            if len(parts) == 2:
                min_price = Decimal(parts[0].strip())
                max_price = Decimal(parts[1].strip())
                return (min_price, max_price)

        return (None, None)
    except (ValueError, TypeError):
        return (None, None)


@login_required
def add_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.save()
            form.save_photos(listing)  # This now works perfectly
            messages.success(request, "New listing added successfully!")
            return redirect('listings')
    else:
        form = ListingForm()
    
    return render(request, 'listings/add_listing.html', {'form': form})


@login_required
def edit_listing_status(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == 'POST':
        form = ListingForm(
            request.POST,
            request.FILES,
            instance=listing
        )

        for field_name in list(form.fields.keys()):
            if field_name != 'status_id':
                form.fields.pop(field_name, None)

        if form.is_valid():
            form.save()
            messages.success(request, "Status updated successfully!")
            return redirect('listings')
    else:
        form = ListingForm(instance=listing)
        for field_name in list(form.fields.keys()):
            if field_name != 'status_id':
                form.fields.pop(field_name, None)

    return render(request, 'listings/add_listing.html', {
        'form': form,
        'listing': listing,
        'is_edit': True
    })
# @login_required
# def add_listing(request):
#     """View to add a new property listing."""
#     from .image_utils import generate_thumbnail, compress_image

#     if request.method == 'POST':
#         form = ListingForm(request.POST, request.FILES)
#         if form.is_valid():
#             listing = form.save(commit=False)
#             listing.created_by = request.user
#             listing.is_visible = True

#             status_value = form.cleaned_data.get('status')
#             if status_value:
#                 status_mapping = {'Available': 'Active', 'Pending': 'Pending', 'Sold': 'Sold'}
#                 status_name = status_mapping.get(status_value)
#                 if status_name:
#                     try:
#                         status_obj = Status.objects.get(name=status_name)
#                         listing.status_id = status_obj
#                     except Status.DoesNotExist:
#                         pass

#             listing.save()

#             photos = request.FILES.getlist('photos')
#             for i, photo_file in enumerate(photos):
#                 image_data = photo_file.read()
#                 compressed_image = compress_image(image_data)
#                 thumbnail = generate_thumbnail(image_data)

#                 Photo.objects.create(
#                     listing=listing,
#                     image_data=compressed_image,
#                     thumbnail_data=thumbnail,
#                     photo_display_order=i+1
#                 )

#             return redirect('listings')
#     else:
#         form = ListingForm()

#     return render(request, 'listings/add_listing.html', {'form': form})


@login_required
def toggle_listing_visibility(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == 'POST':
        action = request.POST.get('visibility')
        if action == 'hide':
            listing.is_visible = False
        elif action == 'show':
            listing.is_visible = True
        else:
            listing.is_visible = not listing.is_visible
        listing.save()

        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('listings')

    context = {'listing': listing}
    return render(request, 'listings/toggle_listing_visibility.html', context)


def custom_logout(request):
    logout(request)
    return render(request, 'accounts/logout.html')


def listing_photo(request, photo_id):
    """View to serve listing photos from binary data."""
    photo = get_object_or_404(Photo, pk=photo_id)
    if photo.image_data:
        image_header = photo.image_data[:8]
        if image_header.startswith(b'\x89PNG\r\n\x1a\n'):
            content_type = 'image/png'
        elif image_header.startswith(b'\xff\xd8\xff'):
            content_type = 'image/jpeg'
        elif image_header.startswith(b'GIF'):
            content_type = 'image/gif'
        else:
            content_type = 'image/png'

        response = HttpResponse(photo.image_data, content_type=content_type)
        response['Cache-Control'] = 'public, max-age=31536000'
        return response
    return HttpResponse(status=404)


def listing_photo_thumbnail(request, photo_id):
    """View to serve listing photo thumbnails from binary data."""
    from .image_utils import generate_thumbnail

    photo = get_object_or_404(Photo, pk=photo_id)

    # Serve existing thumbnail if present
    if getattr(photo, 'thumbnail_data', None):
        response = HttpResponse(photo.thumbnail_data, content_type='image/jpeg')
        response['Cache-Control'] = 'public, max-age=31536000'
        return response

    # If no thumbnail exists, try to generate from image_data
    if getattr(photo, 'image_data', None):
        try:
            thumbnail = generate_thumbnail(photo.image_data)
            if thumbnail:
                # save thumbnail for future requests (best-effort)
                try:
                    photo.thumbnail_data = thumbnail
                    photo.save(update_fields=['thumbnail_data'])
                except Exception:
                    # Do not fail the request if saving fails; log and continue
                    logger.exception("Failed to save generated thumbnail for photo id %s", photo_id)

                response = HttpResponse(thumbnail, content_type='image/jpeg')
                response['Cache-Control'] = 'public, max-age=31536000'
                return response
        except Exception:
            logger.exception("Error generating thumbnail for photo id %s", photo_id)

    return HttpResponse(status=404)


def omaha(request):
    see_do_locations = OmahaLocation.objects.filter(is_published=True, category='See & Do').order_by('display_order', 'name')
    food_locations = OmahaLocation.objects.filter(is_published=True, category='Food').order_by('display_order', 'name')
    event_locations = OmahaLocation.objects.filter(is_published=True, category='Events').order_by('display_order', 'name')

    context = {
        'see_do_locations': see_do_locations,
        'food_locations': food_locations,
        'event_locations': event_locations,
    }
    return render(request, 'omaha.html', context)


@login_required
def manage_omaha(request):
    category_filter = request.GET.get('category')

    locations = OmahaLocation.objects.all().order_by('category', 'display_order', 'name')

    if category_filter:
        locations = locations.filter(category=category_filter)

    context = {
        'locations': locations,
        'current_category': category_filter,
        'categories': ['See & Do', 'Food', 'Events']
    }
    return render(request, 'listings/omaha_manage.html', context)


@login_required
def add_omaha_location(request):
    if request.method == 'POST':
        form = OmahaLocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.created_by = request.user
            location.save()
            return redirect('manage_omaha')
    else:
        form = OmahaLocationForm()

    return render(request, 'listings/omaha_form.html', {
        'form': form,
        'title': 'Add Location to Discover Omaha'
    })


@login_required
def edit_omaha_location(request, location_id):
    """View to edit an existing Omaha location."""
    location = get_object_or_404(OmahaLocation, pk=location_id)

    if request.method == 'POST':
        form = OmahaLocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('manage_omaha')
    else:
        form = OmahaLocationForm(instance=location)

    return render(request, 'listings/omaha_form.html', {
        'form': form,
        'title': 'Edit Location to Discover Omaha',
        'is_edit': True
    })


@login_required
def delete_omaha_location(request, location_id):
    """View to delete an Omaha location."""
    location = get_object_or_404(OmahaLocation, pk=location_id)

    if request.method == 'POST':
        location.delete()
        return redirect('manage_omaha')

    return render(request, 'listings/omaha_delete_confirm.html', {'location': location})




@login_required
def generate_report(request):
    """View for generating monthly search reports."""
    from django.db.models import Count
    from datetime import datetime

    report_data = None
    selected_month = None
    selected_year = None

    if request.method == 'GET' and 'month' in request.GET and 'year' in request.GET:
        try:
            selected_month = int(request.GET.get('month'))
            selected_year = int(request.GET.get('year'))

            # Filter search logs for the selected month/year
            search_logs = SearchLog.objects.filter(
                timestamp__month=selected_month,
                timestamp__year=selected_year
            )

            # Aggregate by property type
            property_type_counts = search_logs.filter(
                property_type__isnull=False
            ).values(
                'property_type__name'
            ).annotate(
                search_count=Count('search_log_id')
            ).order_by('-search_count')

            # Aggregate by neighborhood
            neighborhood_counts = search_logs.filter(
                neighborhood__isnull=False
            ).values(
                'neighborhood__name'
            ).annotate(
                search_count=Count('search_log_id')
            ).order_by('-search_count')

            # Aggregate by price range
            price_range_counts = search_logs.filter(
                pricebucket__isnull=False
            ).values(
                'pricebucket__range'
            ).annotate(
                search_count=Count('search_log_id')
            ).order_by('-search_count')

            report_data = {
                'property_types': list(property_type_counts),
                'neighborhoods': list(neighborhood_counts),
                'price_ranges': list(price_range_counts),
                'month': datetime(selected_year, selected_month, 1).strftime('%B'),
                'year': selected_year,
            }
        except (ValueError, TypeError):
            pass

    # Generate month and year options
    current_year = timezone.now().year
    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    years = range(current_year - 5, current_year + 1)

    context = {
        'report_data': report_data,
        'months': months,
        'years': years,
        'selected_month': selected_month,
        'selected_year': selected_year,
    }

    return render(request, 'listings/generate_report.html', context)


@login_required
def export_report_csv(request):
    """Export the search report as CSV."""
    import csv
    from django.db.models import Count
    from datetime import datetime
    from django.contrib import messages

    if 'month' not in request.GET or 'year' not in request.GET:
        messages.error(request, "Missing month or year parameter.")
        return redirect('generate_report')

    try:
        selected_month = int(request.GET.get('month'))
        selected_year = int(request.GET.get('year'))
    except (ValueError, TypeError):
        messages.error(request, "Invalid month or year parameter.")
        return redirect('generate_report')

    # Filter search logs for the selected month/year
    search_logs = SearchLog.objects.filter(
        timestamp__month=selected_month,
        timestamp__year=selected_year
    )

    # Aggregate data
    property_type_counts = search_logs.filter(
        property_type__isnull=False
    ).values('property_type__name').annotate(
        search_count=Count('search_log_id')
    ).order_by('-search_count')

    neighborhood_counts = search_logs.filter(
        neighborhood__isnull=False
    ).values('neighborhood__name').annotate(
        search_count=Count('search_log_id')
    ).order_by('-search_count')

    price_range_counts = search_logs.filter(
        pricebucket__isnull=False
    ).values('pricebucket__range').annotate(
        search_count=Count('search_log_id')
    ).order_by('-search_count')

    # Check if there's any data to export
    if not property_type_counts and not neighborhood_counts and not price_range_counts:
        month_name = datetime(selected_year, selected_month, 1).strftime('%B')
        messages.warning(request, f"No search data available for {month_name} {selected_year} to create a report.")
        return redirect(f"{reverse('generate_report')}?month={selected_month}&year={selected_year}")

    # Create CSV response
    month_name = datetime(selected_year, selected_month, 1).strftime('%B')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="search_report_{month_name}_{selected_year}.csv"'

    writer = csv.writer(response)
    writer.writerow([f'Search Report for {month_name} {selected_year}'])
    writer.writerow([])

    # Write property type data
    writer.writerow(['Home Type', 'Searches'])
    for item in property_type_counts:
        writer.writerow([item['property_type__name'], item['search_count']])
    writer.writerow([])

    # Write neighborhood data
    writer.writerow(['Neighborhood', 'Searches'])
    for item in neighborhood_counts:
        writer.writerow([item['neighborhood__name'], item['search_count']])
    writer.writerow([])

    # Write price range data
    writer.writerow(['Price Range', 'Searches'])
    for item in price_range_counts:
        writer.writerow([item['pricebucket__range'], item['search_count']])

    return response

def about(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                send_mail(
                    subject=f"Contact Form - {form.cleaned_data['name']}",
                    message=f"Name: {form.cleaned_data['name']}\n"
                            f"Email: {form.cleaned_data['email']}\n\n"
                            f"{form.cleaned_data['message']}",
                    from_email=form.cleaned_data['email'],
                    recipient_list=[settings.CONTACT_EMAIL],
                )
                messages.success(request, "Thank you! Your message has been sent.")
            except BadHeaderError:
                messages.error(request, "Invalid header found.")
            except Exception:
                messages.error(request, "Unable to send message right now.")
            return redirect('about')
    else:
        form = ContactForm()

    return render(request, 'about.html', {'form': form})

class ListingDetailView(FormMixin, DetailView):
    """
    Detail view for a single property that includes Madison's contact form.
    Restricts public data to visible listings to protect hidden drafts.
    """
    model = Listing
    form_class = ContactForm
    template_name = "listings/listing_detail.html"
    context_object_name = "listing"
    pk_url_kwarg = "listing_id"

    def get_queryset(self):
        queryset = (
            Listing.objects.prefetch_related('photos')
                   .select_related('status_id', 'neighborhood', 'property_type')
        )
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        return queryset.filter(is_visible=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('form', self.get_form())
        photos = list(self.object.photos.all())
        context['photos'] = photos
        gallery_photos = photos[:4] if photos else []
        context['gallery_photos'] = gallery_photos
        context['primary_photo'] = gallery_photos[0] if gallery_photos else None
        context['thumbnail_photos'] = gallery_photos
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        listing = self.object
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        message_text = form.cleaned_data["message"]
        property_url = self.request.build_absolute_uri(
            reverse('listing_detail', kwargs={'listing_id': listing.pk})
        )

        subject = f"New inquiry about {listing.address}"
        body = (
            "A new message was submitted from the listing detail page.\n\n"
            f"Listing: {listing.address}\n"
            f"Neighborhood: {listing.neighborhood}\n"
            f"Type: {listing.property_type}\n"
            f"Price: ${listing.price}\n"
            f"Status: {listing.status_display or 'Not specified'}\n"
            f"Property link: {property_url}\n\n"
            f"From: {name} <{email}>\n\n"
            f"Message:\n{message_text}"
        )

        from_email = (
            getattr(settings, "DEFAULT_FROM_EMAIL", None)
            or getattr(settings, "EMAIL_HOST_USER", None)
            or getattr(settings, "CONTACT_EMAIL", None)
        )
        recipient_email = getattr(settings, "CONTACT_EMAIL", None) or from_email

        try:
            send_mail(
                subject,
                body,
                from_email,
                [recipient_email],
                fail_silently=False,
            )
        except Exception:
            messages.error(
                self.request,
                "There was a problem sending your message. Please try again later."
            )
            return self.form_invalid(form)

        messages.success(self.request, "Your message has been sent!")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('listing_detail', kwargs={'listing_id': self.object.pk})
