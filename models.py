from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True),
    email = models.EmailField(unique=True, blank=False),
    username = models.CharField(max_length=24, unique=True, blank=False),
    passwordHash = models.CharField(max_length=32, blank=False),
    birthDate = models.DateField()

class RelStat(models.Model):
    f1id = models.ForeignKey('Users'),
    f2id = models.ForeignKey('Users'),
    stat = models.IntegerField(blank=False)

class Event(models.Model):
    id = models.AutoField(primary_key=True),
    name = models.CharField(max_length=50, blank=False),
    locLong = models.CharField(max_length=10, blank=False),
    locLat = models.CharField(max_length=510, blank=False),
    booking = models.BooleanField(),
    CreatorID = models.ForeignKey('Users'),
    day = birthDate = models.DateField()

class EventType(models.Model):
    id = models.AutoField(primary_key=True),
    name = models.CharField(max_length=15, blank=False)

class UserPref(models.Model):
    uid = models.ForeignKey('Users'),
    etid = models.ForeignKey('EventTypes')

class UserEvent(models.Model):
    uid = models.ForeignKey('Users'),
    eid = models.ForeignKey('Events'),
    stat = models.IntegerField(blank=False)
