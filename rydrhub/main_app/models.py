from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.utils import timezone
import random # Add this import
import string # Add this import
from django.db.models import Max

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  
    category_image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    passengers = models.IntegerField(default=4)
    suitcases = models.IntegerField(default=2)
    speciality = models.TextField(blank=True, null=True) 
    otherspeciality = models.TextField(blank=True, null=True) 
    starting_price = models.IntegerField(default=0)
    category_slug = AutoSlugField(populate_from ="category_name", unique=True)

    def __str__(self):
        return self.category_name


class Vehicle(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    make = models.CharField(max_length=100, blank=True, null=True)
    vehicle_type = models.CharField(max_length=50) 
    vehicle_image = models.ImageField(upload_to='vehicle_images/', blank=True, null=True)
    main_description = models.TextField(blank=True, null=True)
    description1 = models.CharField(max_length=255, blank=True, null=True)
    description2 = models.CharField(max_length=255, blank=True, null=True)
    description3 = models.CharField(max_length=255, blank=True, null=True)
    description4 = models.CharField(max_length=255, blank=True, null=True)
    description5 = models.CharField(max_length=255, blank=True, null=True)
    fuel_type = models.CharField(max_length=50, blank=True, null=True)
    passengers = models.IntegerField(default=4)
    suitcases = models.IntegerField(default=2)
    rental_rate_per_day = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.make} {self.model_name}"
    

class RentalBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    pickup_location = models.CharField(max_length=255)
    return_location = models.CharField(max_length=255)
    pickup_datetime = models.DateTimeField()
    return_datetime = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=255, blank=True, null=True)  
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('upcoming', 'Upcoming'), 
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'), 
        ('confirmed', 'Confirmed'), 
    ]
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    traveler_full_name = models.CharField(max_length=255, blank=True, null=True)
    traveler_phone = models.CharField(max_length=20, blank=True, null=True)
    traveler_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.vehicle.model_name} by {self.user.username}"
    


    