from django.urls import path
from .views import doctors_list, doctor_detail
urlpatterns = [
       path('doctors/', doctors_list, name='doctors_list'),
       path('doctors/<int:doctor_id>/', doctor_detail, name='doctor_detail'),
     
         
]

