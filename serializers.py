from rest_framework import serializers
from Eventak.models import Users

class UsersSerializer(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=24, unique=True, null=True, blank=True)
    passwordHash = models.CharField(max_length=86, null=True, blank=True)
    profilePic = models.TextField()
    birthDate = models.DateField()
    phoneNumber = models.TextField()

    def create(self, validated_data):
        return Users.objects.create(**validated_data)
