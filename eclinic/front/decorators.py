import sys
from urllib.parse import quote

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse


### function to check if the user is logged in admin type or not. If yes, User will continue using the website else he will be redirected to login page ###
def admin_required(function):
    def wrap(request, *args, **kwargs):

        if request.user.is_anonymous:
            return HttpResponseRedirect(reverse('admin:admin_login'))
        elif request.user.is_superuser == True:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('admin:dmin_login'))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


### function to check if the user is logged in or not. If yes, User will continue using the website else he will be redirected to login page ###
def login_required(function):
    def wrap(request, *args, **kwargs):

        if request.user.is_anonymous:
            return redirect('signin', str(request.path_info).strip('/'))
        elif request.user.is_authenticated == True:
            return function(request, *args, **kwargs)
        else:
            # return redirect('login', str(request.path_info).strip('/'))
            return redirect('signin', str(request.path_info).strip('/'))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap