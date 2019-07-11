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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.map, name='map'),
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('signup/', views.Signup, name='Signup'),
    path('signupM/', Phone.Signup, name='Phone Signup'),
    path('myEvents/', views.displayMyEvents, name='My Events'),
    path('myReservations/', views.displayReservations, name='My Reservations'),
    path('myReservationsM/', Phone.displayReservations, name='My Reservations'),
    path('feeds/', views.newsfeed, name='News Feed'),
    path('notifs/', views.notifications, name='Notifications'),
    path('loginm/',Phone.login, name='Phonelogin'),
    path('phone/login/', Phone.PhoneLogin, name="Phonelogin"),
    path('map/', views.map, name='map'),
    path('EventCreate/', views.CreateEvent, name='eventCreate'),
    path('EventGet/', views.Find, name= 'eventGet'),
    path('active/', views.activeEvents, name='getEventsLocation'),
    path('EventView/', views.EventView, name='View Event'),
    path('EventHide/<int:event>/', views.EventHide, name='Hide Event'),
    path('myFriends/', views.showFriends, name='Get Friends to Invite'),
    path('myFriendsM/', Phone.showFriends, name='Get Friends to Invite'),
    path('invite/', views.invite, name='Get Friends to Invite'),
    path('inviteM/', Phone.invite, name='Get Friends to Invite'),
    path('attend/', views.attend, name='attend Event'),
    path('attendM/', Phone.attend, name='attend Event'),
    path('myInvites/', views.myInvitations, name='Get Friends to Invite'),
    path('myInvitesM/', Phone.myInvitations, name='Get Friends to Invite'),
    path('ajax/validate_username/', include('rest_framework.urls', namespace='rest_framework')),
    path('PhoneEventGet/', Phone.Find, name= 'PhoneEventGet'),
    path('requestFriendship/', views.requestFriendship, name= 'Request Friendship'),
    path('requestFriendshipM/', Phone.requestFriendship, name= 'Request Friendship'),
    path('userSearchPage/', views.findUserPage, name= 'Search User Page'),
    path('userSearch/', views.findUser, name= 'Search User'),
    path('userSearchM/', Phone.findUserByUsername, name= 'Search User by Phone'),
    path('userRequests/', views.userRequests, name= 'check friend Request'),
    path('userRequestsM/', Phone.userRequests, name= 'check friend Request'),
    path('acceptFriendRequest/', views.acceptFriendRequest, name= 'accept friend Request'),
    path('acceptFriendRequestM/', Phone.acceptFriendRequest, name= 'accept friend Request'),
    path('hideFriendRequest/', views.hideFriendRequest, name= 'hide friend Request'),
    path('hideFriendRequestM/', Phone.hideFriendRequest, name= 'hide friend Request'),
    path('createTicket/', Phone.createTicket, name= 'Create a Ticket'),
    path('verifyTicket/', Phone.verifyTicket, name= 'Verify a Ticket'),
    path('SearchPrefrence/', views.findPref, name= 'find Preference'),
    path('SearchPrefrenceEV/', views.findPrefEV, name= 'find Preference for Event'),
    path('addPrefrence/', views.addPref, name= 'add Preference'),
    path('createPrefrence/', views.newPref, name= 'new Preference'),
    path('userPage/', views.UserPage, name= 'User Profile Page'),
    path('updateProfilePic/', views.ProfImgAdd, name= 'update Profile Picture'),
    path('displayArtists/', views.displayArtists, name= 'Display Artists'),
    path('cancelEv/Ev<int:event>/', views.CancelEv, name= 'Delete Events'),
    path('cancelRes/Ev<int:event>/', views.CancelRes, name= 'Delete Reservations'),
    path('', views.map, name='map'),
    path('ajax/validate_username/', views.validate_username, name='validate_username'),
    path('ajax/get_Days_Num/', views.GetDaysNum, name='validate_username'),
    path('initDb/', insertItems.init, name='initiate Database'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
