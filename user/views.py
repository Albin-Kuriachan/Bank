import uuid
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser, Profile
from .permission import IsNotAdminOrStaff
from .send_otp import send_otp_email, send_forget_password_mail, regtion_mail
from .serializers import UserSerializer, ProfileUpdateserializer, LoginSerializer, ProfileDisplayserilizer, \
    Emailserializer, ProfileEditserializer, RestPasswordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth import logout
import datetime
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from account.models import Savings_account,AccountApprove
from fixed_deposit.models import FD_Account_Model
from loan.models import Loan_data


class UserEmailVerify(generics.GenericAPIView):
    serializer_class = Emailserializer
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            email = serializer.validated_data.get('email')
            request.session['otp'] = send_otp_email(email)
            request.session['email'] = email
            otp = request.session.get('otp')
            email = request.session.get('email')
            print(otp)
            print('email',email)

            response_data = {
                'Register Profile': request.build_absolute_uri(reverse('user_register')),
                # 'Rest Password': request.build_absolute_uri(reverse('restpassword'))

            }

            return Response({"message": "OTP  sent email successfully","Register Profile":response_data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class UserProfileRegister(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProfileUpdateserializer

    def create(self, request, *args, **kwargs):
        otp = request.session.get('otp')
        print(otp)
        email = request.session.get('email')
        print("email",email)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            entered_otp = serializer.validated_data.get('otp')
            if entered_otp == str(otp):
                serializer.save(email=email)
                serializer.save()
                created_id = serializer.instance.id
                print(created_id)
                open_savings_url = request.build_absolute_uri(reverse('savings', kwargs={'pk': created_id}))
                success_message = "Profile created successfully check email for customer id."
                regtion_mail(email,created_id)
                #
                # del request.session['otp']
                # del request.session['email']
            else:
                success_message = "Invalid OTP"
                open_savings_url = None
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            'Message': success_message,
            'Choose Account type': {
                'Savings Account': open_savings_url,
            }
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

# Patch profile
class UpdateProfileApi(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileEditserializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance,"jj")
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        print(request.data,'jggj')

        if serializer.is_valid():
            serializer.save()
            updated_data = request.data
            return Response({'Message': 'Updated successfully', 'data': updated_data}, status=200)
        return Response({'Message': "Failed to update", "error": serializer.errors}, status=400)


class Dashboard(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = [IsNotAdminOrStaff]
    def get(self, request):
        user = request.user
        profile = Profile.objects.get(email=user.email)
        open_savings_url = request.build_absolute_uri(reverse('savings', kwargs={'pk': profile.id}))
        open_fd_url = request.build_absolute_uri(reverse('choose_fd_type', kwargs={'pk': profile.id}))
        loan = request.build_absolute_uri(reverse('loan'))
        # account_display = request.build_absolute_uri(reverse('userprofiledata'))
        saving_account = request.build_absolute_uri(reverse('saving_account'))
        fixed_deposit = request.build_absolute_uri(reverse('fixed_deposit'))
        loan_account = request.build_absolute_uri(reverse('loan_account'))

        response_data = {
            'Profile' :{
                "name": f"{profile.first_name} {profile.last_name}",
                'customer id': profile.id,
                'email': profile.email,
                'dob': profile.dob,
                'gender': profile.gender,
                'phone': profile.phone,
                'image': profile.image.url if profile.image else None,
                "update profile": request.build_absolute_uri(reverse('updateprofile', kwargs={'pk': profile.id}))
                # 'savings_accounts': [],
                # 'fd_accounts': [],
                # 'loan_data': []
            },


            'Account': {

                # 'Accounts': account_display
                'Saving Account':saving_account,
                'Fixed Deposit':fixed_deposit,
                'Loan':loan_account,
            },

            'Open New Account': {
                'Savings Account': open_savings_url,
                'Fixed Deposit': open_fd_url,
                'Loan': loan,
                # 'Savings Accounts': profile_detail_url,
            },

        }

        return Response(response_data, status=status.HTTP_200_OK)





# Single profile
class UserProfile(APIView):

    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            profile = Profile.objects.get(email=user)
            savings_accounts = Savings_account.objects.filter(user=profile)
            fd_accounts = FD_Account_Model.objects.filter(user=profile,status='ACTIVE')
            loan_accounts = Loan_data.objects.filter(user=profile)

            response_data = {
                "name": f"{profile.first_name} {profile.last_name}",
                'customer id': profile.id,
                'email': profile.email,
                'dob': profile.dob,
                'gender': profile.gender,
                'phone': profile.phone,
                'image': profile.image.url if profile.image else None,
                "update profile": request.build_absolute_uri(reverse('updateprofile', kwargs={'pk': profile.id})),
                'savings_accounts': [],
                'fd_accounts': [],
                'loan_data': []
            }
            for account in savings_accounts:
                response_data['savings_accounts'].append({
                    'savings_account_number': account.account_number,
                    'balance': account.balance,
                    'withdraw': request.build_absolute_uri(reverse('withdraw', kwargs={'pk': account.account_number})),
                    'transfer': request.build_absolute_uri(reverse('saving_fund_transfer', kwargs={'pk': account.account_number})),
                    'transaction history':request.build_absolute_uri(reverse('transaction', kwargs={'pk': account.account_number})),
                    'set transaction limit':request.build_absolute_uri(reverse('set_transaction_limit', kwargs={'pk': account.account_number})),
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
            for loan in loan_accounts:
                response_data['loan_data'].append({
                    'loan': loan.loan_name,
                    'loan account number': loan.loan_account_number,
                    'loan amount': loan.loan_amount,
                    'interest rate': loan.interest_rate,
                    'month': loan.period,
                    'emi': loan.emi,
                    'open date': loan.open_date,
                    'end date': loan.end_date,
                    'end amount': loan.end_amount,
                    'transferred account': loan.to_account,
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
                    login = request.build_absolute_uri(reverse('dashboard'))

                    resp_data = resp_serializer.data

                    resp_data.pop('username', None)
                    resp_data.pop('password', None)

                    resp_data['Login'] = login

                    return Response({"message": "Login successful.", **resp_data}, status=status.HTTP_201_CREATED)

                else:
                    rest = request.build_absolute_uri(reverse('restpassword'))
                    response_data = {

                        'Rest Password': rest,
                    }
                    return Response({"Message": "Invalid password",**response_data}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                register = request.build_absolute_uri(reverse('login_register'))
                response_data = {

                    'Register': register,
                }
                return Response({"Message": "User not found",**response_data}, status=status.HTTP_404_NOT_FOUND)
        else:
            print("kkhkhkhk")
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
            profile=Profile.objects.filter(email=email,approved=True)


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


class LoginPasswordRest(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class =Emailserializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            user = CustomUser.objects.filter(email=email).first()
            if not user:
                return Response({"message": f"No user found with email {email}"}, status=status.HTTP_400_BAD_REQUEST)

            token = str(uuid.uuid4())
            profile_obj = CustomUser.objects.get(email=email)
            profile_obj.reset_password_token = token
            profile_obj.save()
            print('token', token)
            request.session['token'] = token
            request.session['email'] = email
            send_forget_password_mail(email, token)
            # time.sleep(5)
            # messages.success(request, 'Check Your Email To Reset Password')
            return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginPasswordChanage(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RestPasswordSerializer
    def put(self, request,token, *args, **kwargs):
        user = get_object_or_404(CustomUser, reset_password_token=token)
        print(user)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data.get('password')
            print(password)
            user.set_password(password)
            user.reset_password_token = None
            user.save()
            return Response({"message": "Password Reset Successful"}, status=status.HTTP_200_OK)



# class LoginPasswordRest(generics.UpdateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserSerializer
#
#     def put(self, request, *args, **kwargs):
#         otp = request.session.get('otp')
#         email = request.session.get('email')
#
#         if not otp or not email:
#             return Response({"message": "OTP or email not found in session."}, status=status.HTTP_400_BAD_REQUEST)
#
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             entered_otp = serializer.validated_data.get('otp')
#             if entered_otp == str(otp):
#                 user = CustomUser.objects.get(email=email)
#                 password = serializer.validated_data.get('password')
#                 user.set_password(password)
#                 user.save()
#                 return Response(
#                     {"message": "Password changed successfully."}, status=status.HTTP_200_OK
#                 )
#             else:
#                 return Response({"message": "Incorrect OTP entered."}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)