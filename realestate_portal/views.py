from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.validators import validate_email
from django.views.decorators.http import BadHeaderError, send_mail
from listings.forms import ContactForm

@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    return render(request, 'accounts/logout.html')  

def about(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                send_mail(
                    subject=f"Contact Form – {form.cleaned_data['name']}",
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
