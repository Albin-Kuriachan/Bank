import random

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Savings_account, Transaction
from .serializers import SavingsAccountSerializer, UpdateSavingBalanceSerializer, DisplayBalanceSerializer, \
    TransferSavingBalanceSerializer, TransactionSerializer
from user.models import Profile,CustomUser



class SavingsAccountAPIView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = SavingsAccountSerializer

    def post(self, request, pk):
        profile_instance = get_object_or_404(Profile, pk=pk)
        serializer = SavingsAccountSerializer(data=request.data, context={'profile': profile_instance})
        if serializer.is_valid():
            serializer.save(user=profile_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DisplayBalanceAPIView(APIView):
    def post(self, request):
        serializer = DisplayBalanceSerializer(data=request.data)
        if serializer.is_valid():
            account_number = serializer.validated_data.get('account_number')

            try:
                account = Savings_account.objects.get(account_number=account_number)
                user = account.user
                savings_api_url = reverse('savings_balance_update')

                response_data = {
                    "account_number": account.account_number,
                    "balance": account.balance,
                    "name": f"{user.first_name} {user.last_name}",
                    "savings_api_url": request.build_absolute_uri(savings_api_url)
                }
                return Response(response_data)
            except Savings_account.DoesNotExist:
                return Response({"error": "Account does not exist"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateSavingsBalanceAPIView(APIView):
    def put(self, request):
        serializer = UpdateSavingBalanceSerializer(data=request.data)

        if serializer.is_valid():
            account_number = serializer.validated_data.get('account_number')
            balance = serializer.validated_data.get('balance')

            try:
                account = Savings_account.objects.get(account_number=account_number)
                account.balance += balance
                account.save()
                serialized_account = SavingsAccountSerializer(account)

                return Response({
                    "message": "Balance updated successfully",
                    "account": serialized_account.data
                }, status=status.HTTP_200_OK)
            except Savings_account.DoesNotExist:
                return Response({"error": "Account does not exist"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavingsAccountTransfer(APIView):

    def put(self, request):

        serializer = TransferSavingBalanceSerializer(data=request.data)

        if serializer.is_valid():
            payer_account_number = serializer.validated_data.get('payer_account_number')
            receiver_account_number = serializer.validated_data.get('receiver_account_number')
            amount = serializer.validated_data.get('amount')

            try:
                payer = Savings_account.objects.get(account_number=payer_account_number)
                receiver = Savings_account.objects.get(account_number=receiver_account_number)

                if payer.balance < amount:
                    return Response({"error": "Insufficient balance in the payer's account"},
                                    status=status.HTTP_400_BAD_REQUEST)

                if amount < 1:
                    return Response({"error": "Enter a valid amount"}, status=status.HTTP_400_BAD_REQUEST)
                payer.balance -= amount
                receiver.balance += amount
                payer.save()
                receiver.save()

                # payer transaction record
                transaction_record(request,amount,receiver.account_number,payer.balance,type="dr",p=payer)

                # receiver transaction record
                transaction_record(request,amount,payer.account_number,receiver.balance,type="cr",p=receiver)
                serialized_payer = SavingsAccountSerializer(payer)

                return Response({
                    "message": "Transfer successful",
                    "payer_account": serialized_payer.data,
                }, status=status.HTTP_200_OK)


            except Savings_account.DoesNotExist:
                return Response({"error": "Account does not exist"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def transaction_record(request,amount,receiver,balance,type,p):
    cus = Profile.objects.filter(id=p.user.id).first()
    sa = Savings_account.objects.filter(account_number=p.account_number).first()
    while True:
        transaction_id = ''.join(str(random.randint(0, 9)) for _ in range(10))
        if not Transaction.objects.filter(transaction_id=transaction_id).exists():
            transaction_id = Transaction.transaction_id = transaction_id
            break
    data = Transaction(customer=cus,saving_account=sa,amount=amount,account=receiver,
                       balance=balance,transaction_id=transaction_id,type=type)
    data.save()



# class TransactionRecordAPIView(generics.GenericAPIView):
#
#     permission_classes = [IsAuthenticated]
#     serializer_class = TransactionSerializer
#
#     def post(self, request, format=None):
#
#         user = request.user
#         print(user.email)
#         serializer = TransactionSerializer(data=request.data)
#         # sa=Savings_account.objects.get(user=user.id).first()
#         sa = Savings_account.objects.filter(user=user.id).first()
#         customer = Profile.objects.get(id=user.id)
#         print("khk")
#         if serializer.is_valid():
#             print("hi")
#             serializer.validated_data['customer'] =customer
#             serializer.validated_data['user'] =sa
#
#             while True:
#                 transaction_id = ''.join(str(random.randint(0, 9)) for _ in range(10))
#                 if not Transaction.objects.filter(transaction_id=transaction_id).exists():
#                     serializer.validated_data['transaction_id'] = transaction_id
#                     break
#
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

