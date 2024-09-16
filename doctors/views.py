
from django.shortcuts import render
from .models import Doctor, Location, Language
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from datetime import timedelta, datetime
from django.shortcuts import redirect
from django.urls import reverse



def doctors_list(request):
    # Fetch all locations and languages for the filters
    locations = Location.objects.all()
    languages = Language.objects.all()

    # Get the selected filters from the request
    selected_location_id = request.GET.get('location')
    selected_languages = request.GET.getlist('languages')
    selected_consult_modes = request.GET.getlist('consult_modes')
    selected_fees = request.GET.getlist('fees')
    search_query = request.GET.get('search', '')

    # Base queryset
    doctors = Doctor.objects.all()

    # Apply location filter
    if selected_location_id:
        doctors = doctors.filter(location_id=selected_location_id)

    # Apply search query filter
    if search_query:
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(registration_id__icontains=search_query)
        )

    # Apply language filter
    if selected_languages:
        doctors = doctors.filter(languages__in=selected_languages).distinct()

    # Apply consult mode filter
    if selected_consult_modes:
        if 'Hospital Visit' in selected_consult_modes:
            doctors = doctors.filter(hospital_visit=True)
        if 'Online Consult' in selected_consult_modes:
            doctors = doctors.filter(digital_consult=True)

    # Apply fees filter (assuming you have a price range logic)
    if selected_fees:
        fee_ranges = {
            '100-500': (100, 500),
            '500-1000': (500, 1000),
            '1000+': (1000, None)
        }
        filters = Q()
        for fee in selected_fees:
            if fee in fee_ranges:
                min_price, max_price = fee_ranges[fee]
                if max_price:
                    filters |= Q(price__gte=min_price, price__lte=max_price)
                else:
                    filters |= Q(price__gte=min_price)
        doctors = doctors.filter(filters)

    total_doctors = Doctor.objects.count()

    context = {
        'doctors': doctors,
        'locations': locations,
        'languages': languages,
        'doctors_count': total_doctors,
        'selected_location_id': selected_location_id,
        'selected_languages': selected_languages,
        'selected_consult_modes': selected_consult_modes,
        'selected_fees': selected_fees
    }
    return render(request, 'doctors/doctors_list.html', context)


def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(request, 'doctors/doctor_detail.html', {'doctor': doctor})




