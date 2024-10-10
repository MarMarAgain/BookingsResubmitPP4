# booking/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Studio, Booking
from .forms import BookingForm
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils import timezone
from django.core.mail import send_mail
from django.http import HttpResponse
import environ

env = environ.Env()

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

            booking.save()  # Save it to the database

            # Send a confirmation email
            send_mail(
                subject='Booking Confirmation',
                message=f'Dear Artist,\n\n' 
                        f'Thank you for booking {studio.name}.\n'
                        f'Your booking is confirmed for {booking.start_time} to {booking.end_time}.\n'
                        f'Please remember to pay in full on the day your booking takes place by either card or cash.\n'
                        f"We'll see you then!\n\n"
                        f'Dance Cork Firkin Crane reserves the right to refuse entry.',
                from_email=env('DEFAULT_FROM_EMAIL'),
                recipient_list=[form.cleaned_data['email']],
                fail_silently=False,
            )

            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'book_studio.html', {'form': form, 'studio': studio})


def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_confirmation.html', {'booking': booking})


def delete_booking(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        start_time_str = request.POST.get('start_time')

        try:
            # Parse the start time string into a datetime object
            start_time = timezone.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")

            # Try to find the booking
            booking = Booking.objects.get(email=email, start_time=start_time)

            # Retrieve the studio associated with the booking
            studio = booking.studio

            # Delete the booking
            booking.delete()

            # Send a confirmation email
            send_mail(
                subject='Booking Cancellation',
                message=f'Dear Artist,\n\n'
                        f'This is to confirm that you have cancelled your booking for {studio.name} on {start_time}.\n'
                        f'If this is in error, please contact our reception on (021) 450 7487.\n\n'
                        f'We hope to welcome you back another time.\n\n'
                        f"Until then!\n",
                from_email=env('DEFAULT_FROM_EMAIL'),
                recipient_list=[email],
                fail_silently=False,
            )

            # Set a success message to be displayed
            message = "Booking successfully deleted."

        except Booking.DoesNotExist:
            message = "Booking not found. Please check your email and start time."
        except ValueError:
            message = ("Invalid date format. Please use YYYY-MM-DD HH:MM:SS."
                       " Please see your confirmation email for reference.")

        # Render the delete_booking.html with the message
        return render(request, 'delete_booking.html', {'message': message})

    return render(request, 'delete_booking.html')
