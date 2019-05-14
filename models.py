#!/usr/bin/python3
from django.db import models
from passlib.apps import django_context as pwd_context

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    username = models.CharField(max_length=24, unique=True, null=False, blank=False)
    displayName = models.CharField(max_length=16, unique=True, null=False, blank=False)
    passwordHash = models.CharField(max_length=86, null=False, blank=False)
    profilePic = models.TextField()
    birthDate = models.DateField()
    phoneNumber = models.TextField()
    dayCreated = models.DateTimeField(null=True, blank=True)
    verified = models.BooleanField(null=False, blank=False)

    def hash_password(self, password):
        self.passwordHash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.passwordHash)

class RelStat(models.Model):
    f1id = models.ForeignKey('Users', related_name= 'p1', on_delete=models.CASCADE)  #from
    f2id = models.ManyToManyField('Users')  #to
    stat = models.IntegerField(null=False, blank=False)
    time = models.DateTimeField()

class EventTypes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15, null=False, blank=False)
    def __str__(self):
        return self.name
    def findMainParent(self, id):
        p = "b"
        while p!='':
            find = SubEventTypes.objects.all().filter(E2id=id)

class events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField()
    location = models.TextField(max_length=50)
    locLong = models.CharField(max_length=20, null=False, blank=False)
    locLat = models.CharField(max_length=20, null=False, blank=False)
    city = models.CharField(max_length=20, null=False, blank=False)
    booking = models.BooleanField(null=False)
    Creator = models.ForeignKey('Users', on_delete=models.CASCADE)
    timeFrom = models.DateTimeField(null=True, blank=True)
    timeTo = models.DateTimeField(null=True, blank=True)
    ifPlaceNum = models.BooleanField(null=False)
    placeNum = models.IntegerField(null=True, blank=True)  #### check number of of users currently reserved
    EventTypes = models.ManyToManyField('EventTypes')
    dayCreated = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name

class Reservations(models.Model):
    event = models.ForeignKey('events', on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, null=False, blank=False)
    quantity =  models.IntegerField(null=False, blank=False)
    status = models.IntegerField(null=False, blank=False)

class UserRev(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey('events', on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, null=False, blank=False)
    stars = models.IntegerField(null=False, blank=False)
    time = models.DateTimeField(null=False, blank=False)


class SubEventTypes(models.Model):
    E1id = models.ForeignKey('EventTypes', related_name= 'p', on_delete=models.CASCADE) #parent
    E2id = models.ForeignKey('EventTypes', related_name= 'c', on_delete=models.CASCADE) #child

class UserPref(models.Model):
    uid = models.ForeignKey('Users', on_delete=models.CASCADE)
    etid = models.ForeignKey('EventTypes', on_delete=models.CASCADE)

class UserEvent(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, null=False, blank=False)
    event = models.ForeignKey('events', on_delete=models.CASCADE, null=False, blank=False)
    stat = models.IntegerField(null=False, blank=False)
    view = models.BooleanField(null=False, blank=False)
    #time = models.DateTimeField(null=False, blank=False)
