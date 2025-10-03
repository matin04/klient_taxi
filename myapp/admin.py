from django.contrib import admin
from .models import CustomUser,Profile,Trip,Booking

admin.site.register([CustomUser,Profile,Trip,Booking])