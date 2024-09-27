# booking/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Studio, Booking
from .forms import BookingForm

from datetime import datetime
from django.utils.timezone import make_aware
from django.utils import timezone
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
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'book_studio.html', {'form': form, 'studio': studio})


def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_confirmation.html', {'booking': booking})
