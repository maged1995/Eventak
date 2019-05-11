#!/usr/bin/python3
"""Eventak2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views, Phone, insertItems  #remove InsertItems on full deployment
from rest_framework import routers

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.map, name='map'),
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('signup/', views.Signup, name='Signup'),
    path('myEvents/', views.displayMyEvents, name='My Events'),
    path('myReservations/', views.displayReservations, name='My Reservations'),
    path('loginm/',Phone.login, name='Phonelogin'),
    path('phone/login/', Phone.PhoneLogin, name="Phonelogin"),
    path('map/', views.map, name='map'),
    path('EventCreate/', views.CreateEvent, name='eventCreate'),
    path('EventGet/', views.Find, name= 'eventGet'),
    path('ajax/validate_username/', include('rest_framework.urls', namespace='rest_framework')),
    path('PhoneEventGet/', Phone.Find, name= 'PhoneEventGet'),
    path('requestFriendship/', views.Find, name= 'Request Friendship'),
    path('userSearch/', views.findUser, name= 'Search User'),
    path('cancelEv/Ev<int:event>/', views.CancelEv, name= 'Delete Events'),
    path('cancelRes/Ev<int:event>/', views.CancelRes, name= 'Delete Reservations'),
    path('', views.map, name='map'),
    path('ajax/validate_username/', views.validate_username, name='validate_username'),
    path('ajax/get_Days_Num/', views.GetDaysNum, name='validate_username'),
    path('active/', views.activeEvents, name='getEventsLocation'),
    path('initDb/', insertItems.init, name='initiate Database'),
]
