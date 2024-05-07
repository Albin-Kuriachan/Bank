from django.urls import path
from .views import *

urlpatterns = [
    path('savings/<int:pk>/', SavingsAccountAPIView.as_view(), name='savings'),
    path('savings_balance_update/', UpdateSavingsBalanceAPIView.as_view(), name='savings_balance_update'),
    path('display_saving_balance/', DisplayBalanceAPIView.as_view(), name='display_saving_balance'),
    path('saving_fund_transfer/<int:pk>/', SavingsAccountTransfer.as_view(), name='saving_fund_transfer'),
    path('transaction/<int:pk>/', TransactionRecordAPIView.as_view(), name='transaction'),
    path('withdraw/<int:pk>/', WithdrawalAPIView.as_view(), name='withdraw'),

]
