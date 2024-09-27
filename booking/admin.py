# booking/admin.py
from django.contrib import admin
from .models import Studio, Booking
from django.contrib.admin import DateFieldListFilter

# Register the Studio model
@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ('name', 'hourly_rate','capacity')  # Customize the display fields in the admin panel
    search_fields = ('name', 'capacity')  # Search functionality

# Register the Booking model
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('studio', 'studio_capacity', 'start_time', 'end_time', 'is_confirmed')
    list_filter = ('studio', ('start_time', DateFieldListFilter), 'is_confirmed')  # Filter by studio, start date, and confirmation status
    search_fields = ('studio__name', 'name')  # Search by studio name or user

    # Method to display the studio's capacity in the booking admin
    def studio_capacity(self, obj):
        return obj.studio.capacity

    studio_capacity.short_description = 'Studio Capacity'  # Label for the admin panel