from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Vehicle
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicle, RentalBooking 
from datetime import datetime, timedelta
from django.utils import timezone
import razorpay
from rydrhub.settings import RAZORPAY_ID, RAZORPAY_SECRET, EMAIL_HOST_USER
from django.views.decorators.csrf import csrf_exempt
from razorpay.errors import SignatureVerificationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.timezone import make_aware

# Create your views here.

def service_view(request):
    categories = Category.objects.all()
    pickup_location = request.GET.get('pickup_location', '')
    return_location = request.GET.get('return_location', '')
    pickup_datetime = request.GET.get('pickup_datetime', '')
    return_datetime = request.GET.get('return_datetime', '')

    context = {
        'categories': categories,
        'pickup_location': pickup_location,
        'return_location': return_location,
        'pickup_datetime': pickup_datetime,
        'return_datetime': return_datetime,
    }
    return render(request, 'service.html', context)

@login_required(login_url='/login')
def vehicle_list_by_category(request, category_slug):
    category = get_object_or_404(Category, category_slug=category_slug)
    category_name = category.category_name
    vehicles = Vehicle.objects.filter(category=category)
    pickup_location = request.GET.get('pickup_location', '')
    return_location = request.GET.get('return_location', '')
    pickup_datetime = request.GET.get('pickup_datetime', '')
    return_datetime = request.GET.get('return_datetime', '')
    context = {
        'category_name': category_name,
        'vehicles': vehicles,
        'pickup_location': pickup_location,
        'return_location': return_location,
        'pickup_datetime': pickup_datetime,
        'return_datetime': return_datetime,
    }
    return render(request, 'vehicle_list.html', context)

@login_required(login_url='/login')
def rental_detail_view(request, category_slug, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, category__category_slug=category_slug)
    booking = RentalBooking.objects.filter(user=request.user, vehicle=vehicle).last()
    initial_pickup_location = request.GET.get('pickup_location', '')
    initial_return_location = request.GET.get('return_location', '')
    initial_pickup_datetime = request.GET.get('pickup_datetime', '')
    initial_return_datetime = request.GET.get('return_datetime', '')
    initial_fullname = request.GET.get('traveler_full_name', '')
    initial_phone = request.GET.get('traveler_phone', '')       
    initial_email = request.GET.get('traveler_email', '')     

    context = {
        'vehicle': vehicle,
        'booking': booking,
        'initial_pickup_location': initial_pickup_location,
        'initial_return_location': initial_return_location,
        'initial_pickup_datetime': initial_pickup_datetime,
        'initial_return_datetime': initial_return_datetime,
        'initial_fullname': initial_fullname,
        'initial_phone': initial_phone,
        'initial_email': initial_email,
    }
    return render(request, 'rental_detail.html', context)


@login_required(login_url='/login')
def book_car(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == "POST":
        pickup_address = request.POST.get("pickup_address")
        return_address = request.POST.get("return_address")
        pickup_str = request.POST.get("pickup_datetime")     
        return_str = request.POST.get("return_datetime")    
        try:
            pickup_datetime = datetime.strptime(pickup_str, "%Y-%m-%dT%H:%M")
            return_datetime = datetime.strptime(return_str, "%Y-%m-%dT%H:%M")

            pickup_datetime = make_aware(pickup_datetime)
            return_datetime = make_aware(return_datetime)

        except ValueError:
            messages.error(request, "Invalid date/time format. Please use YYYY-MM-DD HH:MM.")
            return redirect("rental_detail", category_slug=vehicle.category.category_slug, vehicle_id=vehicle.id)
        
        now = timezone.now()
        if pickup_datetime < now:
            messages.error(request, "Pickup date and time cannot be in the past.")
            return redirect("rental_detail", category_slug=vehicle.category.category_slug, vehicle_id=vehicle.id)

        if return_datetime <= pickup_datetime:
            messages.error(request, "Return date/time must be after pickup date/time.")
            return redirect("rental_detail", category_slug=vehicle.category.category_slug, vehicle_id=vehicle.id)

        duration = return_datetime - pickup_datetime
        total_days = max(1, duration.days + (1 if duration.seconds > 0 else 0))
        total_cost = vehicle.rental_rate_per_day * total_days
        traveler_full_name = request.POST.get("fullname")
        traveler_phone = request.POST.get("phone")
        traveler_email = request.POST.get("email")

        booking = RentalBooking.objects.create(
            user=request.user,
            vehicle=vehicle,
            pickup_location=pickup_address,
            return_location=return_address,
            pickup_datetime=pickup_datetime,
            return_datetime=return_datetime,
            total_cost=total_cost,
            is_paid=False,
            status="Pending",  
            traveler_full_name=traveler_full_name,
            traveler_phone=traveler_phone,
            traveler_email=traveler_email
        )

        return redirect("payment", booking_id=booking.id)

    return redirect("home")

@login_required(login_url='/login')
def payment_page(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id, user=request.user)
    vehicle = booking.vehicle

    if request.method == 'POST':

        booking.is_paid = True
        booking.status = "Confirmed"
        booking.save()
        messages.success(request, "Payment successful! Your booking is confirmed.")
        return redirect('payment_success')
    
    client = razorpay.Client(auth=(RAZORPAY_ID, RAZORPAY_SECRET))
    booking_amount = int(booking.total_cost * 100)
    booking_currency = 'INR'
    booking_receipt = f'booking_rcptid_{booking.id}'
    order = client.order.create({
        'amount': booking_amount,
        'currency': booking_currency,
        'receipt': booking_receipt,
        'payment_capture': 1
    })

    context = {
        'booking': booking,
        'vehicle': vehicle,
        'phone_number': booking.user.profile.phone if hasattr(booking.user, 'profile') else 'N/A',
        "razorpay_key": RAZORPAY_ID,
        "order_id": order['id'],
        "order_amount": booking_amount,
        "order_currency": booking_currency,
        "order_receipt": booking_receipt,
    }
    return render(request, 'payment.html', context)


@login_required(login_url='/login')
@csrf_exempt
def payment_success(request, booking_id):
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    client = razorpay.Client(auth=(RAZORPAY_ID, RAZORPAY_SECRET))

    try:
        payment_check = client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })

        if payment_check:

            booking = get_object_or_404(RentalBooking, id=booking_id)
            booking.is_paid = True
            booking.payment_id = razorpay_payment_id
            booking.status = "Confirmed"
            booking.save()

            email_body = render_to_string("email.html", {"booking": booking})
            send_mail(
                "Booking Confirmed",
                "Your booking has been successfully confirmed.",
                EMAIL_HOST_USER,
                [booking.user.email],
                fail_silently=False,
                html_message=email_body
            )

            return render(request, "payment_success.html", {"booking": booking})

    except SignatureVerificationError:
        return render(request, "payment_failed.html")


@login_required(login_url='/login')
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id, user=request.user)
    vehicle = booking.vehicle
    return render(request, 'booking_detail.html', {
        'booking': booking,
        'vehicle': vehicle
    })



@login_required(login_url='/login')
@csrf_exempt
def cancel_booking(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id, user=request.user)


    if booking.pickup_datetime - timezone.now() < timedelta(hours=1):
        messages.error(request, "Bookings cannot be cancelled within 1 hours of the pickup time.")
        return redirect('booking_detail', booking_id=booking.id)

    if booking.status == 'Cancelled':
        messages.info(request, "This booking has already been cancelled.")
        return redirect('booking_detail', booking_id=booking.id)

    if request.method == 'POST':
        client = razorpay.Client(auth=(RAZORPAY_ID, RAZORPAY_SECRET))

        if booking.is_paid and booking.payment_id:
            try:
                refund_amount_paise = int(booking.total_cost * 100) 
                
                refund = client.payment.refund(booking.payment_id, {
                    "amount": refund_amount_paise,
                    "speed": "normal" 
                })

                if refund and refund.get('status') in ['processed', 'pending']: 
                    booking.status = 'Cancelled'
                    booking.cancellation_date = timezone.now()
                    booking.save()
                    messages.success(request, f"Booking {booking.id} successfully cancelled. A refund of ₹{booking.total_cost} has been initiated.")

                    email_body = render_to_string("cancellation_email.html", {"booking": booking, "refund_amount": booking.total_cost})
                    send_mail(
                        "Booking Cancellation Confirmation - RydrHub",
                        f"Your booking {booking.id} has been cancelled and a refund initiated.",
                        EMAIL_HOST_USER,
                        [booking.user.email],
                        fail_silently=False,
                        html_message=email_body
                    )
                    return redirect('booking_detail', booking_id=booking.id)
                else:
                    messages.error(request, "Failed to initiate refund. Please contact support.")
                    print(f"Razorpay Refund Response (Failed): {refund}")

            except Exception as e:
                messages.error(request, f"Error processing refund: {e}. Please contact support.")
                print(f"Error during Razorpay refund for booking {booking.id}: {e}")
        else:
            booking.status = 'Cancelled'
            booking.cancellation_date = timezone.now()
            booking.save()
            messages.success(request, f"Booking {booking.id} successfully cancelled (no refund processed as it was not a paid booking or payment ID missing).")
            
            email_body = render_to_string("cancellation_email.html", {"booking": booking})
            send_mail(
                "Booking Cancellation Confirmation - RydrHub",
                f"Your booking {booking.id} has been cancelled.",
                EMAIL_HOST_USER,
                [booking.user.email],
                fail_silently=False,
                html_message=email_body
            )
        
        return redirect('booking_detail', booking_id=booking.id)

    return redirect('booking_detail', booking_id=booking.id)


@login_required(login_url='/login')
def my_bookings_view(request):
    all_bookings = RentalBooking.objects.filter(user=request.user).order_by('-booking_date')
    
    now = timezone.now()
    for booking in all_bookings:
        if booking.status == 'Confirmed' and booking.pickup_datetime > now:
            booking.status = 'Upcoming'
            booking.save()
        elif booking.status in ['Confirmed',"Active","Upcoming"] and booking.pickup_datetime <= now and now < booking.return_datetime:
            booking.status = 'Active'
            booking.save()
        elif booking.status in ['Confirmed',"Active","Upcoming"] and now >= booking.return_datetime:
            booking.status = 'Completed'
            booking.save()

        duration = booking.return_datetime - booking.pickup_datetime
        # booking.duration_days = max(1, duration.days + (1 if duration.seconds > 0 else 0))
        booking.save()
    current_bookings = all_bookings.filter(status__in=['pending', 'confirmed', 'upcoming', 'active'])
    historical_bookings = all_bookings.filter(status__in=['completed', 'cancelled'])
    
    context = {
        'current_bookings': current_bookings,
        'historical_bookings': historical_bookings,
        'current_count': current_bookings.count(),
        'history_count': historical_bookings.count(),

    }
    
    return render(request, 'my_bookings.html', context)
