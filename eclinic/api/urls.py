from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name='api'

urlpatterns = [
    path('getStatesByCountry', csrf_exempt(views.getStatesByCountry), name='getStatesByCountry'),
    path('getCitiesByState', csrf_exempt(views.getCitiesByState), name='getCitiesByState'),
]
