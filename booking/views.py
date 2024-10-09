# booking/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Studio, Booking
from .forms import BookingForm
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils import timezone
from django.core.mail import send_mail
from django.core.mail import send_mail
from django.http import HttpResponse
# from django.contrib.auth.decorators import login_required

# from datetime import datetime, timedelta, time
# get_irish_holidays

# View for home
def home(request):
    return render(request, 'home.html')

def get_unavailable_slots(studio, selected_date):
    """Returns a list of unavailable time slots for a given studio and date."""
    bookings = Booking.objects.filter(
        studio=studio,
        start_time__date=selected_date
    )

    unavailable_slots = []
    for booking in bookings:
        start_hour = booking.start_time.hour
        end_hour = booking.end_time.hour
        unavailable_slots.extend(range(start_hour, end_hour))

    return unavailable_slots


def studio_list(request):
    studios = Studio.objects.all()  # Get all studio objects
    return render(request, 'studio_list.html', {'studios': studios})


def studio_detail(request, studio_id):
    studio = get_object_or_404(Studio, id=studio_id)  # Get studio by ID
    return render(request, 'studio_detail.html', {'studio': studio})


def book_studio(request, studio_id):
    studio = get_object_or_404(Studio, id=studio_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)  # Create a Booking instance but don't save to DB yet
            booking.studio = studio  # Set the studio

            # Convert the times and adjust timezone if necessary
            booking.start_time = timezone.make_aware(datetime.fromisoformat(form.cleaned_data['start_time']))
            booking.end_time = timezone.make_aware(datetime.fromisoformat(form.cleaned_data['end_time']))

            booking.save()  # Now save it to the database

            # Send a confirmation email
            send_mail(
                subject='Booking Confirmation',
                message=f'Thank you for booking {studio.name}.'
                        f'Your booking is confirmed for {booking.start_time} to {booking.end_time}.',
                from_email='your-email@gmail.com',  # Sender's email
                recipient_list=[form.cleaned_data['email']],  # The email entered in the form
                fail_silently=False,
            )

            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'book_studio.html', {'form': form, 'studio': studio})


def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_confirmation.html', {'booking': booking})

def send_test_email(request):
    try:
        send_mail(
            'Test Email Subject',
            'This is a test email from Django.',
            'maryellekeating@gmail.com',  # Make sure this is your EMAIL_HOST_USER
            ['mary@firkincrane.ie'],  # Replace with your test recipient's email
            fail_silently=False,
        )
        return HttpResponse("Test email sent successfully!")
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")