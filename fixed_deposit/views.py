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
            tenure = serializer.validated_data.get('tenure')

            # Calculate maturity amount
            print(interest_data.period)
            period=interest_data.period.split(' ')
            print(period)
            tenure= int(period[0])
            print(tenure)
            maturity_amount = deposit_amount + (interest_data.interest * deposit_amount * tenure) / (100 * 12)

            # Calculate maturity date
            current_date = datetime.now().date()
            maturity_date = current_date + timedelta(days=tenure * 30)  # Assuming 30 days per month

            # Save data to serializer
            serializer.save(user=profile_data,interest_rate=interest_data.interest,tenure=interest_data.period,maturity_amount=maturity_amount, maturity_date=maturity_date)

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
    serializer_class = FDInterestSerializer  # Assuming you have defined the serializer

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
    serializer_class = CloseFDSerializer  # Specify your serializer class

    def put(self, request, pk):
        fd_instance = get_object_or_404(FD_Account_Model, account_number=pk)

        print(fd_instance.status)
        fd_instance.status = "CLOSED"
        fd_instance.save()

        return Response({"message": "FD account closed successfully"})
