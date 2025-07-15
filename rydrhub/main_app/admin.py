from django.contrib import admin
from .models import Category, Vehicle, RentalBooking

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'description', 'passengers', 'suitcases', 'speciality', 'otherspeciality', 'starting_price', 'category_image', 'category_slug')
    fields = ('category_name', 'description', 'passengers', 'suitcases', 'speciality','otherspeciality', 'starting_price', 'category_image')


class VehicleAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'make', 'category', 'fuel_type', 'passengers', 'suitcases', 'rental_rate_per_day', 'vehicle_image')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'make', 'model_name', 'vehicle_type', 'vehicle_image')
        }),
        ('Specifications', {
            'fields': ('fuel_type', 'passengers', 'suitcases')
        }),
        ('Descriptions', {
            'fields': ('main_description', 'description1', 'description2', 'description3', 'description4', 'description5')
        }),
        ('Pricing', {
            'fields': ('rental_rate_per_day',)
        }),
    )


class RentalBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'pickup_datetime', 'return_datetime', 'pickup_location', 'return_location', 'total_cost','booking_date', 'is_paid','payment_id', 'status','traveler_full_name', 'traveler_phone', 'traveler_email')

    readonly_fields = ('booking_date', 'payment_id')

    fieldsets = (
        ('User & Vehicle', {
            'fields': ('user', 'vehicle')
        }),
        ('Pickup & Return Info', {
            'fields': ('pickup_location', 'return_location', 'pickup_datetime', 'return_datetime')
        }),
        ('Payment Details', {
            'fields': ('total_cost', 'is_paid', 'status', 'payment_id', 'booking_date')
        }),
    )



admin.site.site_header = "RydyHub"

admin.site.register(Category, CategoryAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(RentalBooking, RentalBookingAdmin)
