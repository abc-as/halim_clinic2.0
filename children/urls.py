from django.urls import path
from .views import (submit_child_details, child_detail, children_list, child_edit)


urlpatterns = [
    path('submit-child-details/', submit_child_details, name='submit_child_details'),
    path('child/<int:id>/', child_detail, name='child_detail'),
    path('children/', children_list, name='children_list'),
    path('child/<int:id>/edit/', child_edit, name='child_edit'),
]

