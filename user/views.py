from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser, Profile
from .send_otp import send_otp_email
from .serializers import UserSerializer, ProfileUpdateserializer, LoginSerializer, ProfileDisplayserilizer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth import logout
import datetime
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from account.models import Savings_account
from fixed_deposit.models import FD_Account_Model


# class UserProfileRegister(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     queryset = Profile.objects.all()
#     serializer_class = ProfileUpdateserializer


class UserProfileRegister(generics.CreateAPIView):
    # authentication_classes = []
    permission_classes = [AllowAny]
    # queryset = Profile.objects.all()
    serializer_class = ProfileUpdateserializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        success_message = "Profile created successfully."
        created_id = serializer.data.get('id')
        open_savings_url = request.build_absolute_uri(reverse('savings', kwargs={'pk': created_id}))
        # open_fd_url = request.build_absolute_uri(reverse('choose_fd_type', kwargs={'pk': created_id}))
        # open_fd_url = request.build_absolute_uri(reverse('choose_fd_type') + f'{created_id}/')

        response_data = {
            'Message': success_message,
            'Choose Account type': {
                'Savings Account': open_savings_url,
                # 'Fixed Deposit': open_fd_url,
                # 'Savings Accounts': profile_detail_url,
            }
        }

        return Response(response_data, status=status.HTTP_201_CREATED)



# Patch profile
class UpdateProfileApi(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateserializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serlaizer = self.get_serializer(instance, data=request.data, partial=True)

        if serlaizer.is_valid():
            serlaizer.save()
            return Response({'Message': 'Updated successfully'}, status=200)
        return Response({'Message': "Failed to update", "error": serlaizer.errors}, status=400)



# Single profile
class UserProfile(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        print("user",user,user.id)

        try:
            profile = Profile.objects.get(email=user)
            savings_accounts = Savings_account.objects.filter(user=profile)
            fd_accounts = FD_Account_Model.objects.filter(user=profile,status='ACTIVE')
            response_data = {
                "name": f"{profile.first_name} {profile.last_name}",
                'customer id': profile.id,
                'email': profile.email,
                'dob': profile.dob,
                'gender': profile.gender,
                'phone': profile.phone,
                'image': profile.image.url if profile.image else None,
                'savings_accounts': [],
                'fd_accounts': []
            }
            for account in savings_accounts:
                response_data['savings_accounts'].append({
                    'savings_account_number': account.account_number,
                    'balance': account.balance,
                    'withdraw': request.build_absolute_uri(reverse('withdraw', kwargs={'pk': account.account_number})),
                    'transfer': request.build_absolute_uri(reverse('saving_fund_transfer', kwargs={'pk': account.account_number})),
                    'transaction history':request.build_absolute_uri(reverse('transaction', kwargs={'pk': account.account_number})),
                })
            for fd in fd_accounts:
                response_data['fd_accounts'].append({
                    'fd_account_number': fd.account_number,
                    'deposit amount': fd.deposit_amount,
                    'interest rate': fd.interest_rate,
                    'open date': fd.open_date,
                    'tenure': fd.tenure,
                    'maturity amount': fd.maturity_amount,
                    'maturity date': fd.maturity_date,
                    # 'close fd':request.build_absolute_uri(reverse('close_fd') + f'{fd.account_number}/')
                    'close fd':request.build_absolute_uri(reverse('close_fd', kwargs={'pk': fd.account_number}))

                })

            return Response(response_data)
        except Profile.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Savings_account.DoesNotExist:
            return Response({"error": "No savings accounts found for this user"}, status=status.HTTP_404_NOT_FOUND)



# Display all profile
class ProfileDisplayView(generics.ListAPIView):
    # queryset = Profile.objects.all()
    serializer_class = ProfileUpdateserializer



# Login profile
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                user_obj = CustomUser.objects.get(
                    Q(email__iexact=data["username"]) | Q(email__iexact=data["username"])
                )
                if check_password(data["password"], user_obj.password):
                    user_obj.last_login = datetime.datetime.now()
                    user_obj.save()
                    resp_serializer = LoginSerializer(instance=user_obj)
                    return Response(resp_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"Message": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({"Message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


class LoginRegister(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        if Profile.objects.filter(email=email).exists():
            profile=Profile.objects.filter(email=email)
            # serializer.validated_data['first_name'] = profile.first_name
            # serializer.validated_data['last_name'] = profile.last_name

            self.perform_create(serializer)
            return Response({"message": "Profile created successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Not Valid email ."},
                            status=status.HTTP_501_NOT_IMPLEMENTED)



class Dashboard(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        open_savings_url = request.build_absolute_uri(reverse('savings', kwargs={'pk': user.id}))
        open_fd_url = request.build_absolute_uri(reverse('choose_fd_type', kwargs={'pk': user.id}))
        # open_fd_url = request.build_absolute_uri(reverse('choose_fd_type') + f'{created_id}/')

        response_data = {

            'Choose Account type': {
                'Savings Account': open_savings_url,
                'Fixed Deposit': open_fd_url,
                # 'Savings Accounts': profile_detail_url,
            },

        }

        return Response(response_data, status=status.HTTP_200_OK)




