from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout

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
        password = request.POST.get("password")
        passwordconfirmation = request.POST.get("confirm_password")
        
        if password != passwordconfirmation:
            message = "Passwords do not match"
            return render(request, "register.html", {"message": message})
        
        User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
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

def contact(request):
    return render(request,"contact.html")

def my_bookings(request):
    return render(request,'my_bookings.html')