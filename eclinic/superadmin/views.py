from django.shortcuts import render, redirect
from front.decorators import admin_required, login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import datetime, timedelta
from front import models
from front.backends import AuthBackend
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.contenttypes.models import ContentType
import environ

env = environ.Env()
environ.Env.read_env()

# Create your views here
context = {}
context['project_name'] = env("PROJECT_NAME")


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin:dashboard')
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = AuthBackend.authenticate(
            request, username=username, password=password)
        # user = authenticate(request, username=username, password=password)
        if user:
            if user.is_superuser == 1 and user.is_active == 1:
                login(request, user)
                return redirect('admin:dashboard')
            else:
                messages.error(request, 'User is Not an admin.')
                return redirect('admin:admin_login')
        else:
            messages.error(request, 'Please Provide Valid Credentials.')
            return redirect('admin:admin_login')
    else:
        return render(request, "admin/signin.html", context)


@login_required
def admin_logout(request):
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
    return redirect('admin:admin_login')


@admin_required
def dashboard(request):
    return render(request, 'admin/dashboard.html', context)


@login_required
def roleList(request):
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword')
    if keyword:
        result = models.Role.objects.filter(
            Q(name__icontains=keyword), deleted=0).distinct().order_by('-id')
    else:
        result = models.Role.objects.filter(deleted=0).distinct().order_by('-id')
    paginator = Paginator(result, env("PER_PAGE_DATA"))
    result = paginator.page(page)
    context = {'result': result}
    return render(request, 'admin/role/list.html', context)


@login_required
def roleAdd(request):
    content_types = ContentType.objects.prefetch_related('permission_set').filter(
        app_label='front').exclude(model__in=['city', 'country', 'role', 'rolepermission', 'state', 'usertype', 'bloodgroup', 'gender', 'user'])
    context.update({'content_types': content_types})
    if request.method == "POST":
        data = models.Role()
        data.name = request.POST['name']
        data.save()
        role_permission_details = []
        for index, elem in enumerate(request.POST.getlist('permission[]')):
            role_permission_details.append(models.RolePermission(
                permission_id=elem, role_id=data.id, permitted=1))
        models.RolePermission.objects.bulk_create(role_permission_details)
        messages.success(request, 'Role Created Successfully.')
        return redirect('admin:roleList')
    return render(request, 'admin/role/add.html', context)


@login_required
def roleEdit(request, id):
    result = models.Role.objects.get(pk=id)
    context.update({'result': result})
    if request.method == "POST":
        data = models.Role.objects.get(pk=request.POST['id'])
        data.name = request.POST['name']
        data.save()
        messages.success(request, 'Role Updated Successfully.')
        return redirect('admin:roleList')
    return render(request, 'admin/role/edit.html', context)


@login_required
def roleDelete(request, id):
    data = models.Role.objects.get(pk=id)
    data.deleted = 1
    data.save()
    models.RolePermission.objects.filter(role_id=data.id).update(deleted=0)
    return redirect('admin:roleList')


@login_required
def rolePermissions(request, id):
    result = models.Role.objects.get(pk=id)
    content_types = ContentType.objects.prefetch_related('permission_set').filter(
        app_label='front').exclude(model__in=['city', 'country', 'role', 'rolepermission', 'state', 'usertype', 'bloodgroup', 'gender', 'user'])
    role_permissions = models.RolePermission.objects.filter(deleted=0)
    for each in content_types:
        for permissionDetail in each.permission_set.all():
            permissionDetail.permitted = role_permissions.filter(permission_id=permissionDetail.id, role_id=result.id).first(
            ).permitted if role_permissions.filter(permission_id=permissionDetail.id, role_id=result.id).first() is not None else 0
    context.update({'result': result, 'content_types': content_types})
    if request.method == "POST":
        models.RolePermission.objects.filter(
            role_id=request.POST['role_id']).delete()
        role_permission_details = []
        for index, elem in enumerate(request.POST.getlist('permission[]')):
            role_permission_details.append(models.RolePermission(
                permission_id=elem, role_id=request.POST['role_id'], permitted=1))
        models.RolePermission.objects.bulk_create(role_permission_details)
        messages.success(request, 'Role Permission Updated Successfully.')
        return redirect('admin:roleList')
    return render(request, 'admin/role/permissions.html', context)


@login_required
def userList(request):
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword')
    if keyword:
        result = models.User.objects.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(
            email__icontains=keyword) | Q(phone__icontains=keyword) | Q(role__name__icontains=keyword)).exclude(is_superuser=1).distinct().order_by('-id')
    else:
        result = models.User.objects.exclude(is_superuser=1).distinct().order_by('-id')
    paginator = Paginator(result, env("PER_PAGE_DATA"))
    result = paginator.page(page)
    context = {'result': result}
    return render(request, 'admin/user/list.html', context)


@login_required
def userAdd(request):
    roles = models.Role.objects.filter(deleted=0)
    context.update({'roles': roles})
    if request.method == "POST":
        try:
            exist_email = models.User.objects.get(email=request.POST['email'])
        except:
            exist_email = None
        if exist_email is not None:
            messages.error(
                request, "This Email is already exists with an user.")
            return redirect('admin:userAdd')
        try:
            exist_phone = models.User.objects.get(phone=request.POST['phone'])
        except:
            exist_phone = None
        if exist_phone is not None:
            messages.error(
                request, "This Phone number is already exists with an user.")
            return redirect('admin:userAdd')
        if request.POST['password'] != request.POST['conf_password']:
            messages.error(request, "Passwords does not match.")
            return redirect('admin:userAdd')

        full_name_array = request.POST['name'].split(" ", 1)
        first_name = full_name_array[0]
        last_name = full_name_array[len(full_name_array) - 1]

        user = models.User()
        user.username = request.POST['phone']
        user.email = request.POST['email']
        user.phone = request.POST['phone']

        user.name = request.POST['name']
        user.pswd_token = request.POST['password']
        user.password = make_password(request.POST['password'])
        user.role_id = request.POST['role']
        user.is_superuser = 0
        user.is_active = 1
        user.date_joined = datetime.now()
        user.save()
        messages.success(request, "User Created Successfully")
        return redirect('admin:userList')
    return render(request, 'admin/user/add.html', context)


@login_required
def userEdit(request, id):
    result = models.User.objects.get(pk=id)
    roles = models.Role.objects.filter(deleted=0)
    context.update({'result': result, 'roles': roles})
    if request.method == "POST":
        exist_phone = models.User.objects.filter(phone=request.POST['phone']).exclude(id=request.POST['id']).first()
        if exist_phone is not None:
            messages.error(request, 'Phone number already exists with another user.')
            return redirect('admin:userEdit', request.POST['id'])
        exist_email = models.User.objects.filter(email=request.POST['email']).exclude(id=request.POST['id']).first()
        if exist_email is not None:
            messages.error(request, 'Email already exists with another user.')
            return redirect('admin:userEdit', request.POST['id'])
        data = models.User.objects.get(pk=request.POST['id'])
        data.name = request.POST['name']
        data.phone = request.POST['phone']
        data.username = request.POST['phone']
        data.email = request.POST['email']
        data.role_id = request.POST['role']
        data.save()
        messages.success(request, 'User Updated Successfully.')
        return redirect('admin:userList')
    return render(request, 'admin/user/edit.html', context)


@login_required
def specializationList(request):
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword')
    if keyword:
        result = models.Specialization.objects.filter(
            Q(name__icontains=keyword), deleted=0).distinct().order_by('-id')
    else:
        result = models.Specialization.objects.filter(deleted=0).distinct().order_by('-id')
    paginator = Paginator(result, env("PER_PAGE_DATA"))
    result = paginator.page(page)
    context = {'result': result}
    return render(request, 'admin/specialization/list.html', context)


@login_required
def specializationAdd(request):
    if request.method == "POST":
        specialization = models.Specialization()
        specialization.name = request.POST['name']
        specialization.save()
        messages.success(request, 'Specialization Created Successfully.')
        return redirect('admin:specializationList')
    return render(request, 'admin/specialization/add.html', context)


@login_required
def specializationEdit(request, id):
    result = models.Specialization.objects.get(pk=id)
    context.update({'result': result})
    if request.method == "POST":
        data = models.Specialization.objects.get(pk=request.POST['id'])
        data.name = request.POST['name']
        data.save()
        messages.success(request, 'Specialization Updated Successfully.')
        return redirect('admin:specializationList')
    return render(request, 'admin/specialization/edit.html', context)


@login_required
def specializationDelete(request, id):
    data = models.Specialization.objects.get(pk=id)
    data.deleted = 1
    data.save()
    return redirect('admin:specializationList')


@login_required
def languageList(request):
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword')
    if keyword:
        result = models.Language.objects.filter(
            Q(name__icontains=keyword), deleted=0).distinct().order_by('-id')
    else:
        result = models.Language.objects.filter(deleted=0).distinct().order_by('-id')
    paginator = Paginator(result, env("PER_PAGE_DATA"))
    result = paginator.page(page)
    context = {'result': result}
    return render(request, 'admin/language/list.html', context)


@login_required
def languageAdd(request):
    if request.method == "POST":
        exist_language = models.Language.objects.filter(name__icontains=request.POST['name']).first()
        if exist_language is not None:
            messages.error(request, 'This Language is already exists.')
            return redirect('admin:languageAdd')
        language = models.Language()
        language.name = request.POST['name']
        language.save()
        messages.success(request, 'Language Created Successfully.')
        return redirect('admin:languageList')
    return render(request, 'admin/language/add.html', context)


@login_required
def languageEdit(request, id):
    result = models.Language.objects.get(pk=id)
    context.update({'result': result})
    if request.method == "POST":
        exist_language = models.Language.objects.filter(name__icontains=request.POST['name']).exclude(id=request.POST['id']).first()
        if exist_language is not None:
            messages.error(request, 'This Language is already exists.')
            return redirect('admin:languageEdit', request.POST['id'])
        data = models.Language.objects.get(pk=request.POST['id'])
        data.name = request.POST['name']
        data.save()
        messages.success(request, 'Language Updated Successfully.')
        return redirect('admin:languageList')
    return render(request, 'admin/language/edit.html', context)


@login_required
def languageDelete(request, id):
    data = models.Language.objects.get(pk=id)
    data.deleted = 1
    data.save()
    return redirect('admin:languageList')
