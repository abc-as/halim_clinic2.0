from django.urls import path
from .views import available_slots, book_slot


urlpatterns = [
    path('doctor/<int:doctor_id>/slots/', available_slots, name='available_slots'),

    path('doctors/<int:doctor_id>/book/<str:selected_date>/<str:slot_start>/<str:slot_end>/', book_slot, name='book_slot'),

]

