from rest_framework import serializers
from .models import Savings_account, Transaction
import random


class SavingsAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Savings_account
        fields = ['account_number', 'balance']
        read_only_fields = ['account_number']

    def create(self, validated_data):
        while True:
            account_number = ''.join(str(random.randint(0, 9)) for _ in range(8))
            account_number = "11" + account_number
            if not Savings_account.objects.filter(account_number=account_number).exists():
                validated_data['account_number'] = account_number
                break

        return Savings_account.objects.create(**validated_data)


class DisplayBalanceSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=20)


class UpdateSavingBalanceSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class TransactionLimitSerializer(serializers.Serializer):
    transaction_limit = serializers.IntegerField()

    def update(self, instance, validated_data):
        instance.balance = validated_data.get('balance', instance.balance)
        return instance


class TransferSavingBalanceSerializer(serializers.Serializer):
    # payer_account_number = serializers.CharField(max_length=10)
    receiver_account_number = serializers.CharField(max_length=10)
    password = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def update(self, instance, validated_data):
        instance.balance = validated_data.get('balance', instance.balance)
        return instance


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'type','balance','date','transaction_id']


    # def create(self, validated_data):
    #     while True:
    #         transaction_id = ''.join(str(random.randint(0, 9)) for _ in range(10))
    #         if not Transaction.objects.filter(transaction_id=transaction_id).exists():
    #             validated_data['transaction_id'] = transaction_id
    #             break

# class WithdrawalSerializer(serializers.Serializer):
#     amount = serializers.DecimalField(max_digits=5,decimal_places=0)
#     password = serializers.CharField(max_digits=10)

class WithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
    password = serializers.CharField(max_length=128)

class DepositSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
