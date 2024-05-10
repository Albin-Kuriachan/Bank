from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from .models import Different_Loan, Loan_Interest_Period, Loan_data
from .serializers import DifferentLoanSerializer, LoanInterstPeriodSerializer, ApplyLoanSerializers, CD, \
    CloseLoanSerializer, LoanPymentSerializers
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import Profile
from account.models import Savings_account

from account.views import transaction_record


class DifferentLoanView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Different_Loan.objects.all()
    serializer_class = DifferentLoanSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        response_data = []

        for item in data:
            item_data = item.copy()
            loan_url = reverse('loan_detail', kwargs={'loan_name': item_data["loan_name"]})
            item_data["Choose Loan"] = request.build_absolute_uri(loan_url)
            response_data.append(item_data)

        return Response(response_data)


class LoanInterestPeriod(APIView):
    permission_classes = [AllowAny]

    def get(self, request, loan_name):
        loan = get_object_or_404(Different_Loan, loan_name=loan_name)
        loan_interest_periods = Loan_Interest_Period.objects.filter(loan_name=loan)

        loan_data_serializer = DifferentLoanSerializer(loan)

        interest_periods_data = []
        for interest_period in loan_interest_periods:
            interest_periods_data.append({
                'amount limit': interest_period.amount_limit,
                'period': interest_period.loan_period,
                'interest rate': interest_period.loan_interest,
                'Choose Loan': request.build_absolute_uri(reverse('loan_apply', kwargs={'pk': interest_period.id})),
            })
        loan_data = {
            'Loan ': loan_data_serializer.data,
            'Interest and Periods': interest_periods_data
        }
        return Response(loan_data, status=status.HTTP_200_OK)


class LoanApply(APIView):
    def post(self, request, pk):

        user = request.user
        profile_data = get_object_or_404(Profile, email=user)
        lip = Loan_Interest_Period.objects.get(id=pk)
        loan_account_exists = Loan_data.objects.filter(loan_name=lip.loan_name).exists()

        # if loan_account_exists:
        #     error_message = f"There is pending {lip.loan_name}"
        #     return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ApplyLoanSerializers(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data.get('loan_amount')
            period = serializer.validated_data.get('period')
            to_account = serializer.validated_data.get('to_account')
            # loan_account_number = serializer.validated_data.get('loan_account_number')
            # print(loan_account_number,'loan_account_number')
            # to_account_data=Savings_account.objects.filter(account_number=to_account)
            to_account_data = get_object_or_404(Savings_account, account_number=to_account)
            to_account_validate = Savings_account.objects.filter(account_number=to_account, user=profile_data).exists()
            if not to_account_validate:
                error_message = f"{to_account} is not your saving account "
                return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

            loan_amount_split = lip.amount_limit.split('-')
            from_amount = int(loan_amount_split[0])
            to_amount = int(loan_amount_split[1])

            loan_period_split = lip.loan_period.split('-')

            from_month = int(loan_period_split[0])
            to_month = int(loan_period_split[1])

            if amount < from_amount or amount > to_amount:
                error_message = f"Enter a amount between {from_amount} and {to_amount}"
                return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

            if period < from_month or period > to_month:
                error_message = f"Enter a month between {from_month} and {to_month}"
                return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

            interest_rate = lip.loan_interest
            interest = (amount * interest_rate / 100)
            emi = amount / period + interest
            end_amount = emi * period
            current_date = datetime.now().date()
            end_date = current_date + relativedelta(months=period)

            serializer.save(user=profile_data, interest_rate=interest_rate, end_date=end_date,
                            end_amount=end_amount, emi=emi, loan_name=lip.loan_name, current_balance=end_amount)
            created_id = serializer.instance.id
            loan_account = get_object_or_404(Loan_data, id=created_id)
            serialized_loan_account = CD(loan_account).data

            to_account_data.balance += amount
            to_account_data.save()
            transaction_record(request, amount, loan_account.loan_account_number, to_account_data.balance, type='cr',
                               p=to_account_data, transaction_type=lip.loan_name)
            return Response(serialized_loan_account, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Loan accounts display
class LoanAccount(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        response_data = {'loan_data': []}

        try:
            profile = Profile.objects.get(email=user)
            loan_accounts = Loan_data.objects.filter(user=profile, status='ACTIVE')
            # saving_account_data = request.build_absolute_uri(reverse('saving_account_data'))

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
                    'balance to pay': loan.current_balance,
                    # 'loan payment':loan_payment,
                    # 'loan payment': request.build_absolute_uri(reverse('saving_account_data', kwargs={'pk': loan.loan_account_number})),
                    'loan payment': request.build_absolute_uri(
                        reverse('saving_account_data', kwargs={'pk': loan.loan_account_number}))

                })

        except Profile.DoesNotExist:
            pass

        return Response(response_data)


class CloseLoan(generics.UpdateAPIView):

    def calculate_close_amount(self, loan_instance):
        # current_date = datetime.now().date()
        print(loan_instance.open_date)
        print(loan_instance.close_date)
        active_period = loan_instance.close_date - loan_instance.open_date
        active_days = active_period.days
        print(active_days)
        total_interest = (loan_instance.loan_amount * loan_instance.interest_rate * active_days) / (365 * 100)
        total_interest = round(total_interest, 2)
        close_amount = loan_instance.loan_amount + total_interest
        return close_amount

    def put(self, request, pk, sa):
        loan_instance = get_object_or_404(Loan_data, loan_account_number=pk)
        from_account = get_object_or_404(Savings_account, account_number=sa)
        current_date = datetime.now().date()

        if loan_instance.status == "CLOSED":
            return Response({"message": "This account is already closed"})

        if from_account.balance < loan_instance.current_balance:
            return Response(f"message : {from_account.account_number} balance lesser than amount to payment amount")

        loan_instance.status = "CLOSED"
        loan_instance.close_date = current_date
        loan_instance.from_account = from_account.account_number
        # close_amount = self.calculate_close_amount(loan_instance)
        close_amount = loan_instance.current_balance
        loan_instance.current_balance = 0
        loan_instance.close_amount = close_amount
        loan_instance.save()
        from_account.balance -= close_amount
        from_account.save()
        transaction_record(request, close_amount, loan_instance.loan_account_number, from_account.balance, type="dr",
                           p=from_account, transaction_type='loanclose')
        loan_instances = get_object_or_404(Loan_data, loan_account_number=pk)
        serializer = CloseLoanSerializer(loan_instances)

        return Response(
            # {"message": "Loan closed successfully"})
            {"message": "Loan closed successfully", "close_amount": close_amount, "Details": serializer.data})


class Loanpayment(generics.UpdateAPIView):
    serializer_class = LoanPymentSerializers

    def put(self, request, pk, sa):
        loan_instance = get_object_or_404(Loan_data, loan_account_number=pk)
        from_account = get_object_or_404(Savings_account, account_number=sa)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data.get('amount')
            print(amount, 'amount')
            loan_instance.current_balance -= amount
            loan_instance.save()
            from_account.balance -= amount
            from_account.save()
            transaction_record(request, amount, loan_instance.loan_account_number, from_account.balance,
                               type="dr",
                               p=from_account, transaction_type='loan payment')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
