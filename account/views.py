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
    TransferSavingBalanceSerializer, TransactionSerializer, WithdrawalSerializer
from user.models import Profile,CustomUser
from django.contrib.auth.hashers import check_password



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
    permission_classes = [IsAuthenticated]
    def put(self, request,pk):
        user = request.user
        # save_account=Savings_account.objects.filter(account_number=pk)
        serializer = TransferSavingBalanceSerializer(data=request.data)
        print(pk)
        if serializer.is_valid():
            password = serializer.validated_data.get('password')
            # payer_account_number = serializer.validated_data.get('payer_account_number')
            payer_account_number = pk
            receiver_account_number = serializer.validated_data.get('receiver_account_number')
            amount = serializer.validated_data.get('amount')

            if check_password(password, user.password):

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
                    transaction_record(request,amount,payer.account_number,
                                       receiver.account_number,payer.balance,type="dr",p=payer)

                    # receiver transaction record
                    transaction_record(request,amount,payer.account_number,receiver.account_number,
                                       receiver.balance,type="cr",p=receiver)
                    serialized_payer = SavingsAccountSerializer(payer)

                    return Response({
                        "message": "Transfer successful",
                        "payer_account": serialized_payer.data,
                    }, status=status.HTTP_200_OK)


                except Savings_account.DoesNotExist:
                    return Response({"error": "Account does not exist"}, status=status.HTTP_404_NOT_FOUND)
            else:

                return Response({"error": "Invalid password"},status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def transaction_record(request,amount,receiver,payer,balance,type,p):
    # cus = Profile.objects.filter(id=p.user.id).first()
    cus = Profile.objects.get(id=p.user.id)
    # sa = Savings_account.objects.filter(account_number=p.account_number).first()
    sa = Savings_account.objects.get(account_number=p.account_number)
    while True:
        transaction_id = ''.join(str(random.randint(0, 9)) for _ in range(10))
        if not Transaction.objects.filter(transaction_id=transaction_id).exists():
            transaction_id = Transaction.transaction_id = transaction_id
            break
    data = Transaction(customer=cus,saving_account=sa,amount=amount,payer_account=receiver,
                       receiver_account=payer,balance=balance,transaction_id=transaction_id,type=type)

    data.save()



class TransactionRecordAPIView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    # def get(self, request,pk,format=None,):
    #     user = request.user
    #     print(user.email)
    #     transaction_data = Transaction.objects.filter(account=pk)

    def get(self, request, pk, format=None):
        user = request.user
        profile = Profile.objects.get(email=user)
        transaction_data = Transaction.objects.filter(payer_account=pk,customer=profile)
        serializer = self.serializer_class(transaction_data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



class WithdrawalAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request,pk):
        user=request.user
        serializer = WithdrawalSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            password = serializer.validated_data['password']
            if check_password(password, user.password):
                account = Savings_account.objects.get(account_number=pk)
                if account.balance >= amount:
                    account.balance -= amount
                    account.save()
                    return Response({'message': 'Withdrawal successful', 'balance': account.balance}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
            else:

                return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




