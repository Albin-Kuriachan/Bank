from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from datetime import datetime, timedelta
from .models import Interest_Table, FD_Account_Model
from .serializers import FDAccountSerializer, FDInterestSerializer, CloseFDSerializer
from user.models import Profile


# create fd account

class FDAccountAPIView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = FDAccountSerializer

    def post(self, request, pk,id):
        interest_data = get_object_or_404(Interest_Table, id=id)
        profile_data = get_object_or_404(Profile, pk=pk)
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            deposit_amount = serializer.validated_data.get('deposit_amount')
            amount = serializer.validated_data.get('amount')

            # Calculate maturity amount
            print(interest_data.period)
            period=interest_data.period.split(' ')
            print(period)
            tenure= int(period[0])
            print(tenure)
            maturity_amount = deposit_amount + (interest_data.interest * deposit_amount * tenure) / (100 * 12)

            # Calculate maturity date
            current_date = datetime.now().date()
            maturity_date = current_date + timedelta(days=tenure * 30)

            # Save data to serializer
            serializer.save(user=profile_data,interest_rate=interest_data.interest,tenure=interest_data.period,
                            maturity_amount=maturity_amount, maturity_date=maturity_date,current_balance=amount)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Display all fd account
class FDdetailsview(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = FD_Account_Model.objects.all()
    serializer_class = FDAccountSerializer


# Display  fd interest rate
class FDInterestview(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Interest_Table.objects.all()
    serializer_class = FDInterestSerializer


class Choose_Fd(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = FDInterestSerializer

    def list(self, request, pk, *args, **kwargs):
        queryset = Interest_Table.objects.all()
        serializer = self.get_serializer(queryset, many=True)

        response_data = []
        for interest_data in serializer.data:
            fd_url = reverse('fd', kwargs={'pk': pk,'id': interest_data["id"]})
            interest_data["Fixed Deposit"] = request.build_absolute_uri(fd_url)
            response_data.append(interest_data)
        return Response(response_data, status=status.HTTP_200_OK)





class Close_FD(generics.UpdateAPIView):
    serializer_class = CloseFDSerializer

    def calculate_close_amount(self, fd_instance):
        # current_date = datetime.now().date()
        print(fd_instance.open_date)
        print(fd_instance.close_date)
        active_period = fd_instance.close_date - fd_instance.open_date
        print('active',active_period)
        active_days = active_period.days
        print('active_days',active_days)
        total_interest = (fd_instance.deposit_amount * fd_instance.interest_rate * active_days) / (365 * 100)
        total_interest = round(total_interest, 2)
        print('total_interest',total_interest)
        close_amount = fd_instance.deposit_amount + total_interest
        print('close_amount',close_amount)

        return close_amount

    # def put(self, request, pk):
    #     fd_instance = get_object_or_404(FD_Account_Model, account_number=pk)
    #     current_date = datetime.now().date()
    #     if fd_instance.status == "CLOSED":
    #         return Response({"message": "FD account is already closed"})
    #     fd_instance.status = "CLOSED"
    #     fd_instance.current_balance = 0
    #     fd_instance.close_date = current_date
    #     close_amount = self.calculate_close_amount(fd_instance)
    #     fd_instance.close_amount = close_amount
    #     fd_instance.save()
    #
    #     return Response({"message": "FD account closed successfully", "close_amount": close_amount})

    def put(self, request, pk):
        fd_instance = get_object_or_404(FD_Account_Model, account_number=pk)
        current_date = datetime.now().date()

        if fd_instance.status == "CLOSED":
            return Response({"message": "FD account is already closed"})

        fd_instance.status = "CLOSED"
        fd_instance.current_balance = 0
        fd_instance.close_date = current_date
        close_amount = self.calculate_close_amount(fd_instance)
        fd_instance.close_amount = close_amount
        fd_instance.save()

        # Retrieve all the data including the closed FD account
        fd_instances = get_object_or_404(FD_Account_Model, account_number=pk)
        serializer = CloseFDSerializer(fd_instances)

        return Response(
            {"message": "FD account closed successfully", "close_amount": close_amount, "data": serializer.data})