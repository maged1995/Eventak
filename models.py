#!/usr/bin/python3
from django.db import models
from passlib.apps import custom_app_context as pwd_context

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=24, unique=True, null=True, blank=True)
    passwordHash = models.TextField(max_length=32, null=True, blank=True)
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
    stat = models.IntegerField(null=True, blank=True)

class Events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField()
    location = models.TextField(max_length=50)
    locLong = models.CharField(max_length=10, null=True, blank=True)
    locLat = models.CharField(max_length=10, null=True, blank=True)
    booking = models.BooleanField()
    CreatorID = models.ForeignKey('Users', on_delete=models.CASCADE)
    day = models.DateField()

class EventTypes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15, null=True, blank=True)

class UserPref(models.Model):
    uid = models.ForeignKey('Users', on_delete=models.CASCADE)
    etid = models.ForeignKey('EventTypes', on_delete=models.CASCADE)

class UserEvent(models.Model):
    uid = models.ForeignKey('Users', on_delete=models.CASCADE)
    eid = models.ForeignKey('Events', on_delete=models.CASCADE)
    stat = models.IntegerField(null=True, blank=True)
