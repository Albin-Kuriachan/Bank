import random
from rest_framework import serializers
from .models import Different_Loan,Loan_Interest_Period,Loan_data



class DifferentLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Different_Loan
        fields = ['loan_name']

class LoanInterstPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Different_Loan
        fields = ['loan_name','loan_interest','loan_period']


class ApplyLoanSerializers(serializers.ModelSerializer):
    # amount = serializers.IntegerField()
    # period = serializers.IntegerField()
    class Meta:
        model = Loan_data
        fields = ['loan_amount', 'period','loan_account_number','to_account']
        read_only_fields = ['loan_account_number']

    def create(self, validated_data):

        while True:
            loan_account_number = ''.join(str(random.randint(0, 9)) for _ in range(8))
            loan_account_number = "55" + loan_account_number
            if not Loan_data.objects.filter(loan_account_number=loan_account_number).exists():
                validated_data['loan_account_number'] = loan_account_number
                break
        return Loan_data.objects.create(**validated_data)

class CD(serializers.ModelSerializer):
    class Meta:
        model = Loan_data
        exclude = ['id','user','current_balance','status','from_account','close_amount','close_date']

class CloseLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan_data
        exclude = ['id','user']

class LoanPymentSerializers(serializers.Serializer):
    amount = serializers.IntegerField()
