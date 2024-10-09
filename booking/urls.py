# booking/urls.py

from django.urls import path
from .views import book_studio,booking_confirmation, studio_list, studio_detail
from django.urls import path


urlpatterns = [
    path('studios/', studio_list, name='studio_list'),  # Accessible at /booking/studios/
    path('studios/<int:studio_id>/', studio_detail, name='studio_detail'),  # Accessible at /booking/studios/<studio_id>/
    path('studios/<int:studio_id>/book/', book_studio, name='book_studio'),  # Accessible at /booking/studios/<studio_id>/book/
    path('confirmation/<int:booking_id>/', booking_confirmation, name='booking_confirmation'),  # Accessible at /booking/confirmation/<booking_id>/,
]
