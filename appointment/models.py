from django.db import models
from doctors.models import Doctor
from accounts.models import CustomUser
# Create your models here.


class Booking(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')  # Assuming a user model
    slot_start = models.TimeField()
    slot_end = models.TimeField()
    date = models.DateField()

    class Meta:
        unique_together = ('doctor', 'slot_start', 'slot_end', 'date')
    def __str__(self):
        return f"{self.doctor.name} - {self.slot_start} to {self.slot_end} on {self.date}"
