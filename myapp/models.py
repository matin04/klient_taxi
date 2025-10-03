from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('taxi', 'Taxi'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.username



class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_bookings = models.IntegerField(default=0)

    def __str__(self):
        return self.user


class Trip(models.Model):
    taxi = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    date = models.DateTimeField()
    seats = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.origin

class Booking(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    seats_booked = models.IntegerField()

    def __str__(self):
        return self.seats_booked