import random

from rest_framework import serializers
from django.core.exceptions import ValidationError
from user.models import CustomUser

from .models import StaffProfile
from user.models import Profile


class StaffSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('staff_id','email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_staff(**validated_data)
        return user

    def validate(self, data):
        if 'staff_id' not in data:
            raise serializers.ValidationError("staff_id is required")
        return data

class Emailserializer(serializers.Serializer):
    email =serializers.EmailField()

class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = ['id','personal_email','first_name', 'last_name', 'dob', 'gender', 'phone']

    def validate(self, data):
        return data


    def create(self, validated_data):
        email = f"{validated_data['first_name'].lower()}.{validated_data['last_name'].lower()}@bank.com"

        if StaffProfile.objects.filter(email=email).exists():
            random_digit = random.randint(0, 9)
            email = f"{email[:-9]}{random_digit}@bank.com"

        validated_data['email'] = email
        instance = super().create(validated_data)
        return instance

    # def create(self, validated_data):
    #     email = f"{validated_data['first_name'].lower()}.{validated_data['last_name'].lower()}@bank.com"
    #     if StaffProfile.objects.filter(email=email).exists():
    #         raise ValidationError("Email ID already exists")
    #     validated_data['email'] = email
    #     instance = super().create(validated_data)
    #     return instance

class ProfileApproveSerializer (serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = "__all__"
