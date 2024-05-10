from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from rest_framework import generics, status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import StaffProfile
from .serializers import Emailserializer, StaffSerializer, StaffProfileSerializer, ProfileApproveSerializer
from  user.send_otp import send_otp_email,regtion_mail_staff

from user.permission import IsAdminOrStaff

from user.models import Profile


# Create your views here.

class StaffProfileRegister(generics.CreateAPIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = StaffProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            created_id = serializer.instance.id
            success_message = "Staff Profile created successfully."
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        staff_profile = get_object_or_404(StaffProfile, pk=created_id)

        staff_login_register = request.build_absolute_uri(reverse('staff_login_register'))
        regtion_mail_staff(staff_profile.personal_email,created_id,staff_profile.email,staff_login_register)
        response_data = {
            'Message': success_message,
            # 'Choose Account type': {
            # }
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class StaffLoginRegister(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = StaffSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        if StaffProfile.objects.filter(email=email).exists():
            profile=StaffProfile.objects.filter(email=email,approved=True)


            if profile:
                self.perform_create(serializer)
                login = request.build_absolute_uri(reverse('login'))
                response_data = {

                    'Login': login,
                }
                return Response({"message": "Profile created successfully.", **response_data},
                                status=status.HTTP_201_CREATED)

            else:
                return Response({"message": "Your profile is not verified try later."}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error": "Not Valid email ."},
                            status=status.HTTP_501_NOT_IMPLEMENTED)



class ApproveProfile(generics.UpdateAPIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        profiles = Profile.objects.filter(approved=False)
        serializer = ProfileApproveSerializer(profiles, many=True)  # Use your serializer
        profiles_with_links = []
        for profile in serializer.data:
            # Assuming the approval function is named 'approve_profile'
            profile_url = request.build_absolute_uri(reverse('approve_profile', args=[profile['id']]))
            profile['approve_now'] = profile_url
            profiles_with_links.append(profile)

        response_data = {
            'profiles': profiles_with_links,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, profile_id):
        profile = Profile.objects.get(id=profile_id)
        profile.approved = True
        profile.save()
        return Response({"message": f"Profile {profile_id} has been approved"}, status=status.HTTP_200_OK)