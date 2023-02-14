from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('forgot-password', views.forgot, name='forgot'),
    path('enter_otp', views.enter_otp, name='enter_otp'),
    path('password_reset', views.password_reset, name='password_reset'),
]
