import random

from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from rest_framework import status, generics,serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Savings_account, Transaction, AccountApprove
from .serializers import SavingsAccountSerializer, UpdateSavingBalanceSerializer, DisplayBalanceSerializer, \
    TransferSavingBalanceSerializer, TransactionSerializer, WithdrawalSerializer, DepositSerializer, \
    TransactionLimitSerializer
from user.models import Profile, CustomUser
from django.contrib.auth.hashers import check_password

from user.send_otp import send_email


class SavingsAccountAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SavingsAccountSerializer

    def post(self, request, pk):
        profile_instance = get_object_or_404(Profile, pk=pk)
        serializer = SavingsAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=profile_instance)
            created_id = serializer.instance
            print(created_id)
            approve = AccountApprove(saving_account=created_id)
            approve.save()

            return Response({"message": "Balance updated successfully", "Account Details": serializer.data},status=status.HTTP_201_CREATED)

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
                    "c": account.balance,
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
            amount = serializer.validated_data.get('amount')

            try:
                account = Savings_account.objects.get(account_number=account_number)
                account.balance += amount
                account.save()
                transaction_record_wd(request, amount, account_number, account.balance, type="cr",
                                      transaction_type='deposit')

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

    def put(self, request, pk):
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

                    if amount > payer.transaction_limit  :
                        return Response({"error": "Higher than transaction limit"},
                                        status=status.HTTP_400_BAD_REQUEST)

                    if payer.balance < amount and payer.balance < payer.transaction_limit:
                        return Response({"error": "Insufficient balance t"},
                                        status=status.HTTP_400_BAD_REQUEST)

                    if amount < 1:
                        return Response({"error": "Enter a valid amount"}, status=status.HTTP_400_BAD_REQUEST)
                    payer.balance -= amount
                    receiver.balance += amount
                    payer.save()
                    receiver.save()

                    # payer transaction record
                    transaction_record(request, amount, receiver.account_number, payer.balance, type="dr", p=payer,
                                       transaction_type='tranfer')

                    # receiver transaction record
                    transaction_record(request, amount, payer.account_number, receiver.balance, type="cr", p=receiver,
                                       transaction_type='tranfer')

                    serialized_payer = SavingsAccountSerializer(payer)

                    return Response({
                        "message": "Transfer successful",
                        "payer_account": serialized_payer.data,
                    }, status=status.HTTP_200_OK)


                except Savings_account.DoesNotExist:
                    return Response({"error": "Account does not exist"}, status=status.HTTP_404_NOT_FOUND)
            else:

                return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def transaction_record(request, amount, account_data, balance, type, p, transaction_type):
    cus = Profile.objects.get(id=p.user.id)
    sa = Savings_account.objects.get(account_number=p.account_number)
    while True:
        transaction_id = ''.join(str(random.randint(0, 9)) for _ in range(10))
        if not Transaction.objects.filter(transaction_id=transaction_id).exists():
            transaction_id_number = Transaction.transaction_id = transaction_id
            break

    transaction_id = f"{transaction_type}/{transaction_id_number}/{account_data}"
    data = Transaction(customer=cus, saving_account=sa, amount=amount,
                       balance=balance, transaction_id=transaction_id, type=type)


    data.save()

    send_email(cus.email,type,amount,sa.account_number,balance)


class SetTransactionLimit(generics.GenericAPIView):
    def put(self, request, pk):
        serializer = TransactionLimitSerializer(data=request.data)
        if serializer.is_valid():
            transaction_limit = serializer.validated_data.get('transaction_limit')
            # Retrieve the savings account based on the provided pk
            saving_account = get_object_or_404(Savings_account, account_number=pk)
            # Update the transaction limit
            saving_account.transaction_limit = transaction_limit
            saving_account.save()
            return Response({"message": f"Transaction limit updated to {transaction_limit} successfully"},status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class TransactionRecordAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get(self, request, pk, format=None):
        transaction_data = Transaction.objects.filter(saving_account__account_number=pk)
        transaction_data = transaction_data.order_by('-id')
        serializer = self.serializer_class(transaction_data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class WithdrawalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        serializer = WithdrawalSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            password = serializer.validated_data['password']
            if check_password(password, user.password):
                account = Savings_account.objects.get(account_number=pk)
                if account.balance >= amount:
                    account.balance -= amount
                    account.save()
                    transaction_record_wd(request, amount, account.account_number, account.balance, type="dr",transaction_type='withdraw')

                    return Response({'message': 'Withdrawal successful', 'balance': account.balance},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
            else:

                return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def transaction_record_wd(request, amount, account, balance, type, transaction_type):
    sa = Savings_account.objects.get(account_number=account)
    while True:
        transaction_id = ''.join(str(random.randint(0, 9)) for _ in range(10))
        if not Transaction.objects.filter(transaction_id=transaction_id).exists():
            transaction_id_number = Transaction.transaction_id = transaction_id
            break

    transaction_id = f"{transaction_type}/{transaction_id_number}"
    data = Transaction(customer=sa.user, saving_account=sa, amount=amount, balance=balance,
                       transaction_id=transaction_id, type=type)
    data.save()


# class DepositAPIView(generics.UpdateAPIView):
#     serializer_class = DepositSerializer
#
#     def put(self, request):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             account_number = serializer.validated_data.get('account_number')
#             amount = serializer.validated_data.get('amount')
#             saving_account = get_object_or_404(Savings_account, account_number=account_number)
#             saving_account.balance += amount
#             saving_account.save()
#             transaction_record_wd(request, amount, account_number, saving_account.balance, type="cr",transaction_type='deposit')
#             return Response({"message": "Deposit successful", "data": serializer.data}, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# savings accounts display

class SavingAccount(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        response_data = {'savings_accounts': []}  # Initialize response_data

        try:
            profile = Profile.objects.get(email=user)
            savings_accounts = Savings_account.objects.filter(user=profile)

            for account in savings_accounts:
                response_data['savings_accounts'].append({
                    'savings_account_number': account.account_number,
                    'balance': account.balance,
                    'withdraw': request.build_absolute_uri(reverse('withdraw', kwargs={'pk': account.account_number})),
                    'transfer': request.build_absolute_uri(reverse('saving_fund_transfer', kwargs={'pk': account.account_number})),
                    'transaction_history': request.build_absolute_uri(reverse('transaction', kwargs={'pk': account.account_number})),
                    'set_transaction_limit': request.build_absolute_uri(reverse('set_transaction_limit', kwargs={'pk': account.account_number})),
                })

        except Profile.DoesNotExist:
            pass

        return Response(response_data)


class SavingAccountData(APIView):
    def get(self, request,pk, *args, **kwargs):
        user = request.user
        response_data = {'savings_accounts': []}

        try:
            profile = Profile.objects.get(email=user)
            savings_accounts = Savings_account.objects.filter(user=profile)

            for account in savings_accounts:
                response_data['savings_accounts'].append({
                    'savings_account_number': account.account_number,
                    'balance': account.balance,
                    'choose account to pay': request.build_absolute_uri(reverse('loan_payment', kwargs={'sa': account.account_number,'pk':pk})),
                    'choose account to close loan': request.build_absolute_uri(reverse('close_loan', kwargs={'sa': account.account_number,'pk':pk}))
                })
        except Profile.DoesNotExist:
            pass

        return Response(response_data)

