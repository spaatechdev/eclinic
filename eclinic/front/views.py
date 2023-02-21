from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from front.backends import AuthBackend
from django.contrib import messages
from decimal import Decimal
from .decorators import login_required
from eclinic import settings
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from . import models
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password, check_password
from eclinic.settings import MEDIA_ROOT, MEDIA_URL
from django.utils import timezone
import os
import json
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
        username = request.POST['username']
        password = request.POST['password']
        user = AuthBackend.authenticate(
            request, username=username, password=password)
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
    return render(request, 'back/dashboard.html', context)


@login_required
def doctorList(request):
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword')
    if keyword:
        result = models.User.objects.prefetch_related('doctordetail_set').filter(
            Q(name__icontains=keyword)).filter(role__name="Doctor").distinct().order_by('-id')
    else:
        result = models.User.objects.prefetch_related('doctordetail_set').filter(
            role__name="Doctor").distinct().order_by('-id')
    paginator = Paginator(result, env("PER_PAGE_DATA"))
    result = paginator.page(page)
    languages = models.Language.objects.filter(deleted=0)
    context = {'result': result, 'languages': languages}
    return render(request, 'back/doctor/list.html', context)


@login_required
def doctorAdd(request):
    specializations = models.Specialization.objects.filter(deleted=0)
    bloodGroups = models.BloodGroup.objects.filter(deleted=0)
    genders = models.Gender.objects.filter(deleted=0)
    countries = models.Country.objects.filter(pk=101)
    languages = models.Language.objects.filter(deleted=0)
    role = models.Role.objects.filter(name="Doctor").first()
    context.update({
        'genders': genders,
        'specializations': specializations,
        'bloodGroups': bloodGroups,
        'countries': countries,
        'languages': languages,
        'role': role
    })
    if request.method == "POST":
        exist_phone = models.User.objects.filter(phone=request.POST['phone']).first()
        if exist_phone is not None:
            messages.error(request, 'This Phone is already exists with another user.')
            return redirect('doctorAdd')
        exist_email = models.User.objects.filter(phone=request.POST['email']).first()
        if exist_email is not None:
            messages.error(request, 'This Email is already exists with another user.')
            return redirect('doctorAdd')
        if request.FILES and request.FILES['profile_pic'] is not None:
            file = request.FILES['profile_pic']
            tmpname = str(datetime.now(tz=timezone.utc).microsecond) + \
                os.path.splitext(str(file))[1]
            fs = FileSystemStorage(
                MEDIA_ROOT + env("MEDIA_PROFILES"), MEDIA_ROOT + env("MEDIA_PROFILES"))
            fs.save(tmpname, file)
        user = models.User()
        user.username = request.POST['phone']
        user.email = request.POST['email']
        user.phone = request.POST['phone']
        user.name = request.POST['name']
        user.password = make_password(request.POST['password'])
        user.role_id = request.POST['role']
        user.is_superuser = 0
        user.is_active = 1
        user.date_joined = datetime.now()
        user.save()

        doctor = models.DoctorDetail()
        doctor.dob = request.POST['dob']
        doctor.address = request.POST['address']
        doctor.locality = request.POST['locality']
        doctor.pin = request.POST['pin']
        doctor.alternate_number = request.POST['alternate_number']
        doctor.language_id = request.POST['language']
        doctor.blood_group_id = request.POST['blood_group']
        doctor.specialization_id = request.POST['specialization']
        doctor.city_id = request.POST['city']
        doctor.state_id = request.POST['state']
        doctor.country_id = request.POST['country']
        doctor.gender_id = request.POST['gender']
        doctor.user_id = user.id
        doctor.profile_pic = MEDIA_URL + env("MEDIA_PROFILES") + tmpname
        doctor.save()

        messages.success(request, 'doctor Created Successfully.')
        return redirect('doctorList')
    return render(request, 'back/doctor/add.html', context)


@login_required
def doctorEdit(request, id):
    result = models.User.objects.prefetch_related(
        'doctordetail_set').get(pk=id)
    specializations = models.Specialization.objects.filter(deleted=0)
    bloodGroups = models.BloodGroup.objects.filter(deleted=0)
    genders = models.Gender.objects.filter(deleted=0)
    countries = models.Country.objects.filter(pk=101)
    states = models.State.objects.filter(
        country_id=result.doctordetail_set.all()[0].country_id)
    cities = models.City.objects.filter(
        state_id=result.doctordetail_set.all()[0].state_id)
    languages = models.Language.objects.filter(deleted=0)
    role = models.Role.objects.filter(name="Doctor").first()
    context.update({'result': result, 'specializations': specializations, 'bloodGroups': bloodGroups, 'genders': genders,
                   'countries': countries, 'states': states, 'cities': cities, 'languages': languages, 'role': role})
    if request.method == "POST":
        exist_phone = models.User.objects.filter(phone=request.POST['phone']).exclude(id=request.POST['id']).first()
        if exist_phone is not None:
            messages.error(request, 'This Phone is already exists.')
            return redirect('doctorAdd')
        exist_email = models.User.objects.filter(phone=request.POST['email']).exclude(id=request.POST['id']).first()
        if exist_email is not None:
            messages.error(request, 'This Email is already exists.')
            return redirect('doctorAdd')
        if request.FILES and request.FILES['profile_pic'] is not None:
            file = request.FILES['profile_pic']
            tmpname = str(datetime.now(tz=timezone.utc).microsecond) + \
                os.path.splitext(str(file))[1]
            fs = FileSystemStorage(
                MEDIA_ROOT + env("MEDIA_PROFILES"), MEDIA_ROOT + env("MEDIA_PROFILES"))
            fs.save(tmpname, file)
        user = models.User.objects.get(pk=request.POST['id'])
        user.username = request.POST['phone']
        user.email = request.POST['email']
        user.phone = request.POST['phone']
        user.name = request.POST['name']
        user.save()

        doctor = models.DoctorDetail.objects.get(user_id=user.id)
        if doctor is None:
            doctor = models.DoctorDetail()
        doctor.dob = request.POST['dob']
        doctor.address = request.POST['address']
        doctor.locality = request.POST['locality']
        doctor.pin = request.POST['pin']
        doctor.alternate_number = request.POST['alternate_number']
        doctor.language_id = request.POST['language']
        doctor.blood_group_id = request.POST['blood_group']
        doctor.specialization_id = request.POST['specialization']
        doctor.city_id = request.POST['city']
        doctor.state_id = request.POST['state']
        doctor.country_id = request.POST['country']
        doctor.gender_id = request.POST['gender']
        doctor.user_id = user.id
        if request.FILES and request.FILES['profile_pic'] is not None:
            doctor.profile_pic = MEDIA_URL + env("MEDIA_PROFILES") + tmpname
        doctor.save()
        messages.success(request, 'Doctor Updated Successfully.')
        return redirect('doctorList')
    return render(request, 'back/doctor/edit.html', context)


@login_required
def doctorDelete(request, id):
    data = models.doctor.objects.get(pk=id)
    data.deleted = 1
    data.save()
    return redirect('doctorList')
