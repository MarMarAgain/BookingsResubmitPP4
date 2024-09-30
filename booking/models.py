# booking/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import time, timedelta, date
from django.core.exceptions import ValidationError
from decimal import Decimal


class Studio(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    blurb = models.TextField(max_length=150, default='Please enter a brief description of the studio')
    description = models.TextField()
    benefits = models.TextField(
        help_text="Comma-separated list of recommended activities for the studio (e.g. Yoga, Photography, Dance)",
        default="Rehersal"
    )
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=20, help_text="Hourly rate for the studio")  # Fixed rate
    capacity = models.IntegerField()
    image = models.ImageField(upload_to='studios/', default='logo.png')

    def __str__(self):
        return self.name

    def get_recommended_uses(self):
        """Return recommended uses as a list."""
        return self.benefits.split(',') if self.benefits else []

class Booking(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)
    name = models.CharField(max_length=100, default='Name Needed')
    email = models.EmailField(default='default@example.com')
    phone_number = models.CharField(max_length=20, default='000-000-0000')

    def __str__(self):
        return f'{self.name} - {self.studio.name} ({self.start_time} to {self.end_time})'

    @property
    def total_cost(self):
        # Calculate the duration as the difference between end_time and start_time
        duration = self.end_time - self.start_time

        # Extract total hours from the timedelta
        hours = Decimal(duration.total_seconds()) / Decimal(3600)  # Convert to hours

        # Calculate total cost
        return hours * Decimal(self.studio.hourly_rate)

    def clean(self):
        super().clean()

        # Ensure start_time and end_time are accessible
        if not self.start_time or not self.end_time:
            return

        opening_time = time(10, 0)  # 10:00 AM
        closing_time = time(16, 0)  # 4:00 PM

        if self.start_time.time() < opening_time or self.end_time.time() > closing_time:
            raise ValidationError(_("Bookings must be between 10 AM and 4 PM."))

        if self.start_time.weekday() >= 5:  # Prevent bookings on weekends
            raise ValidationError(_("Bookings cannot be made on weekends."))

        if self.start_time.date() in get_irish_holidays():
            raise ValidationError(_("Bookings cannot be made on public holidays."))

        if Booking.objects.filter(
                studio=self.studio,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
        ).exists():
            raise ValidationError(_("The studio is already booked during this time."))

def get_irish_holidays(year=None):
    """Returns a set of Irish public holidays."""
    if year is None:
        year = timezone.now().year

    return {
        date(year, 1, 1),   # New Year's Day
        date(year, 3, 17),  # St. Patrick's Day
        date(year, 12, 25), # Christmas
        date(year, 12, 26), # St. Stephen's Day
        # Add more fixed or dynamically calculated holidays
    }

