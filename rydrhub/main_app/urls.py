from django.urls import path
from . import views


urlpatterns = [
    path('service/', views.service_view, name='service'),
    path('vehicles/<str:category_slug>/', views.vehicle_list_by_category, name='vehicle_list_by_category'),
    path('vehicles/<str:category_slug>/<int:vehicle_id>/', views.rental_detail_view, name='rental_detail'),
    path('vehicle/<int:vehicle_id>/book/', views.book_car, name='book_car'),
    path('booking/<int:booking_id>/payment/', views.payment_page, name='payment'),
    path('payment/success/<str:booking_id>', views.payment_success, name='payment_success'),
    path('booking/<int:booking_id>/confirmed/', views.booking_detail_view, name='booking_detail'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
  
]