from django import forms
from datetime import datetime, timedelta

from .models import Booking


class BookingForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Booking Date")
    start_time = forms.ChoiceField(choices=[], label="Start Time")
    end_time = forms.ChoiceField(choices=[], label="End Time")

    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone_number','studio','date', 'start_time', 'end_time']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Generate time slot choices
        self.fields['start_time'].choices = self.get_time_slot_choices()
        self.fields['end_time'].choices = self.get_time_slot_choices()

    def get_time_slot_choices(self):
        # Define opening and closing times
        opening_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        closing_time = opening_time.replace(hour=16, minute=0)

        time_slots = []
        current_time = opening_time

        while current_time <= closing_time:
            time_slot_str = current_time.strftime('%Y-%m-%dT%H:%M')  # Use ISO format for input
            display_time_str = current_time.strftime('%H:%M')  # Display format, e.g., 10:00
            time_slots.append((time_slot_str, display_time_str))
            current_time += timedelta(minutes=30)  # Increment by 30 minutes

        return time_slots


def clean(self):
    cleaned_data = super().clean()
    start_time = cleaned_data.get("start_time")
    end_time = cleaned_data.get("end_time")
    date = cleaned_data.get("date")  # Make sure you are capturing the date too

    if date and start_time and end_time:
        # Combine date with time for correct ISO format
        start_time = f"{date}T{start_time.split('T')[1]}"  # Only get the time part
        end_time = f"{date}T{end_time.split('T')[1]}"

        try:
            start_time = datetime.fromisoformat(start_time)
            end_time = datetime.fromisoformat(end_time)
        except ValueError:
            raise forms.ValidationError("Invalid start or end time format.")

        # Ensure the end time is after the start time
        if end_time <= start_time:
            raise forms.ValidationError("End time must be after start time.")

    return cleaned_data


