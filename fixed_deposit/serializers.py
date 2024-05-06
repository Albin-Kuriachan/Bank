from rest_framework import serializers
from .models import FD_Account_Model, Interest_Table
import random


class FDAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FD_Account_Model
        fields = [ 'account_number', 'deposit_amount', 'interest_rate', 'tenure', 'maturity_amount','maturity_date']
        read_only_fields = ['account_number']

    def create(self, validated_data):

        while True:
            account_number = ''.join(str(random.randint(0, 9)) for _ in range(8))
            account_number = "33" + account_number
            if not FD_Account_Model.objects.filter(account_number=account_number).exists():
                validated_data['account_number'] = account_number
                break

        return FD_Account_Model.objects.create(**validated_data)


class FDInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest_Table
        fields = ['id', 'period', 'interest']

class CloseFDSerializer(serializers.ModelSerializer):
    class Meta:
        model = FD_Account_Model
        fields = ['status']