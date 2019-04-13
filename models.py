#!/usr/bin/python3
from django.db import models
from passlib.apps import django_context as pwd_context

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    username = models.CharField(max_length=24, unique=True, null=False, blank=False)
    passwordHash = models.CharField(max_length=86, null=False, blank=False)
    profilePic = models.TextField()
    birthDate = models.DateField()
    phoneNumber = models.TextField()

    def hash_password(self, password):
        self.passwordHash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.passwordHash)

class RelStat(models.Model):
    f1id = models.ForeignKey('Users', related_name= 'p1', on_delete=models.CASCADE)
    f2id = models.ForeignKey('Users', related_name= 'p2', on_delete=models.CASCADE)
    stat = models.IntegerField(null=False, blank=False)

class events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField()
    location = models.TextField(max_length=50)
    locLong = models.CharField(max_length=10, null=False, blank=False)
    locLat = models.CharField(max_length=10, null=False, blank=False)
    city = models.CharField(max_length=20, null=False, blank=False)
    booking = models.BooleanField(null=False)
    Creator = models.ForeignKey('Users', on_delete=models.CASCADE)
    timeFrom = models.DateTimeField()
    timeTo = models.DateTimeField()
    ifPlaceNum = models.BooleanField(null=False)
    placeNum = models.IntegerField(null=True, blank=True)

class reservations(models.Model):
    event = models.ForeignKey('events', on_delete=models.CASCADE)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    quantity =  models.IntegerField(null=False, blank=False)
    status = models.IntegerField(null=False, blank=False)

class EventTypes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15, null=False, blank=False)
    def findMainParent(self, id):
        p = "b"
        while p!='':
            find = SubEventTypes.objects.all().filter(E2id=id)



class SubEventTypes(models.Model):
    E1id = models.ForeignKey('EventTypes', related_name= 'p', on_delete=models.CASCADE) #parent
    E2id = models.ForeignKey('EventTypes', related_name= 'c', on_delete=models.CASCADE) #child

class UserPref(models.Model):
    uid = models.ForeignKey('Users', on_delete=models.CASCADE)
    etid = models.ForeignKey('EventTypes', on_delete=models.CASCADE)

class UserEvent(models.Model):
    uid = models.ForeignKey('Users', on_delete=models.CASCADE)
    eid = models.ForeignKey('Events', on_delete=models.CASCADE)
    stat = models.IntegerField(null=False, blank=False)
