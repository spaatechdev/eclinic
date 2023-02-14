from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from front.backends import AuthBackend
from django.contrib import messages
from decimal import Decimal
from .decorators import login_required
from eclinic import settings
from django.core.mail import send_mail
from . import models
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password, check_password
import math
import random
import environ

env = environ.Env()
environ.Env.read_env()

# Create your views here.
context = {}
context['project_name'] = env("PROJECT_NAME")

def signin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser == 1 and request.user.is_active == 1:
            login(request, request.user)
            return redirect('admin:dashboard')
        else:
            return redirect('signout')
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['password']
        user = AuthBackend.authenticate(request, username=username, password=password)
        if user:
            role_permissions = list(models.RolePermission.objects.filter(role_id=user.role_id, permitted=1).values(
                'permission_id', 'permission__name', 'permission__codename', 'permitted'))
            request.session['role_permissions'] = role_permissions
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please Provide Valid Credentials.')
            return redirect('signin')
    return render(request, 'front/signin.html', context)


def forgot(request):
    if request.method == "POST":
        email = request.POST['email']
        user = models.User.objects.filter(email=email).first()
        if user is not None:
            digits = [i for i in range(0, 10)]
            otp = ""
            for i in range(6):
                index = math.floor(random.random() * 10)
                otp += str(digits[index])
            request.session['OTP'] = otp
            request.session['FORGOT_EMAIL'] = email
            subject = 'OTP for Password Reset'
            message = "This is your One time Password to allow you to reset your password <strong>" + otp + "</strong>"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [request.POST['email']]
            send_mail(subject, message, email_from, recipient_list)
            return redirect('enter_otp')
        else:
            messages.error(request, 'User not found by this email.')
            return redirect('forgot')
    return render(request, "front/forgot_password.html", context)


def enter_otp(request):
    if request.method == "POST":
        if (request.POST['verify_otp'] == request.session['OTP']):
            messages.success(request, "OTP verified!!")
            return redirect('password_reset')
        else:
            messages.error(request, "OTP is not correct")
            return redirect('enter_otp')
    return render(request, "front/enter_otp.html", context)


def password_reset(request):
    if request.method == "POST":
        if (request.POST['password'] == request.POST['confirmpassword']):
            user = models.User.objects.get(
                email=request.session['FORGOT_EMAIL'])
            user.pswd_token = request.POST['password']
            user.password = make_password(request.POST['password'])
            user.save()
            try:
                del request.session
            except:
                pass
            messages.success(request, "Password updated!!")
            return redirect('signin')
        else:
            messages.error(request, "Passwords do not match")
            return redirect('password_reset')
    return render(request, "front/password_reset.html", context)


def signup(request):
    if request.method == "POST":
        try:
            exist_email = models.User.objects.get(email=request.POST['email'])
        except:
            exist_email = None
        if exist_email is None:
            user = models.User()
            user.username = request.POST['email']
            user.email = request.POST['email']
            user.phone = request.POST['phone']
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.pswd_token = request.POST['password']
            user.password = make_password(request.POST['password'])
            user.is_superuser = 0
            user.is_active = 1
            user.date_joined = datetime.now()
            user.save()
            messages.success(
                request, 'Thank you for registering. Please Signin and continue to dashboard')
            return redirect('signin')
        else:
            messages.error(request, 'This Email is already exists.')
            return redirect('signup')
    return render(request, 'front/signup.html', context)


def signout(request):
    logout(request)
    try:
        del request.session
    except:
        pass
    try:
        storage = messages.get_messages(request)
        for message in storage:
            message = ''
        storage.used = False
    except:
        pass
    messages.warning(request, 'Logout Successfully.')
    return redirect('signin')


def home(request):
    return render(request, 'front/home.html', context)

def dashboard(request):
    return render(request, 'admin/dashboard.html', context)
