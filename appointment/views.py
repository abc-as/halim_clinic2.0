from django.shortcuts import render
from doctors.models import Doctor
from django.shortcuts import get_object_or_404
from .models import Booking
from datetime import datetime
from django.shortcuts import redirect
from django.contrib import messages

def available_slots(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    selected_date = request.GET.get('selected_date', timezone.now().date())
    day_of_week_str = timezone.datetime.strptime(selected_date, '%Y-%m-%d').strftime('%A')
    weekly_slots = doctor.generate_weekly_slots()
    all_slots_for_day = weekly_slots.get(day_of_week_str, [])
    booked_slots = Booking.objects.filter(doctor=doctor, date=selected_date).values_list('slot_start', 'slot_end')
    available_slots = [
        slot for slot in all_slots_for_day if not any(
            start == slot[0] and end == slot[1] for start, end in booked_slots
        )
    ]
    
    return render(request, 'appointment/available_slots.html', {
        'doctor': doctor,
        'available_slots': available_slots,
        'selected_date': selected_date,
    })

def book_slot(request, doctor_id, selected_date, slot_start, slot_end):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    slot_start = datetime.strptime(slot_start, "%H:%M:%S").time()
    slot_end = datetime.strptime(slot_end, "%H:%M:%S").time()
    selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    if Booking.objects.filter(doctor=doctor, slot_start=slot_start, slot_end=slot_end, date=selected_date).exists():
        messages.error(request, 'Slot is already booked.')
        return redirect('available_slots', doctor_id=doctor_id, selected_date=selected_date)

    # Create a booking
    booking = Booking.objects.create(
        doctor=doctor,
        user=request.user,
        slot_start=slot_start,
        slot_end=slot_end,
        date=selected_date
    )

    messages.success(request, 'Slot booked successfully.')
    return redirect('available_slots', doctor_id=doctor_id, selected_date=selected_date)