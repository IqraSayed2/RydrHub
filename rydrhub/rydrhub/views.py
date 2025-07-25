from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.shortcuts import render,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from main_app.models import UserProfile


def home(request):
    return render(request,"index.html")

def register(request):
    if request.method == "GET":
        return render(request, "register.html")
    elif request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        passwordconfirmation = request.POST.get("confirm_password")
        
        if password != passwordconfirmation:
            message = "Passwords do not match"
            return render(request, "register.html", {"message": message})
        
        if User.objects.filter(username=username).exists():
            message = "Username already taken"
            return render(request, "register.html", {"message": message})
        
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        UserProfile.objects.create(user=user, phone=phone)

        message = "Registered Successful"
        return render(request, "register.html", {"message": message})
    

def user_login(request):
    if request.method == "GET":
        return render(request,"login.html")
    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username,password=password)
        message = None
        if user is not None:
            login(request,user)
            return HttpResponseRedirect("/")
        message = "Login Failed"
        return render(request,"login.html",{"message":message})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/login")


def faqs(request):
    return render(request,"faq.html")


@login_required(login_url='/login')
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('contact-form-name')
        email = request.POST.get('contact-form-email')
        phone = request.POST.get('contact-form-phone')
        subject = request.POST.get('contact-form-subject')
        message = request.POST.get('contact-form-message')

        print("Contact form submitted:", name, email, subject)

        messages.success(request, "Your message has been sent successfully! Our customer support team will respond to your case as soon as possible.")
        return redirect('contact') 
    return render(request, 'contact.html')


@login_required(login_url='/login')
def my_bookings(request):
    return render(request,'my_bookings.html')


@login_required(login_url='/login')
def view_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {
        'user': request.user,
        'profile': profile
    })


from django.shortcuts import redirect

@login_required(login_url='/login')
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.save()

        profile.phone = request.POST.get('phone')
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()

        return redirect('profile')

    return render(request, 'edit_profile.html', {
        'user': request.user,
        'profile': profile
    })


def about(request):
    return render(request,"about.html")