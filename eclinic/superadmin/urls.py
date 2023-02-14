from django.urls import path, re_path
from . import views

app_name = 'admin'
urlpatterns = [
    re_path(r'^login/', views.admin_login, name='admin_login'),
    re_path(r'^logout/', views.admin_logout, name='admin_logout'),

    path('', views.dashboard, name='dashboard'),

    path('userList', views.userList, name='userList'),
    path('userAdd', views.userAdd, name='userAdd'),
    path('userEdit/<int:id>', views.userEdit, name='userEdit'),

    path('roleList', views.roleList, name='roleList'),
    path('roleAdd', views.roleAdd, name='roleAdd'),
    path('roleEdit/<int:id>', views.roleEdit, name='roleEdit'),
    path('roleDelete/<int:id>', views.roleDelete, name='roleDelete'),
    path('rolePermissions/<int:id>', views.rolePermissions, name='rolePermissions'),

    path('specializationList', views.specializationList, name='specializationList'),
    path('specializationAdd', views.specializationAdd, name='specializationAdd'),
    path('specializationEdit/<int:id>', views.specializationEdit, name='specializationEdit'),
    path('specializationDelete/<int:id>', views.specializationDelete, name='specializationDelete'),
]
