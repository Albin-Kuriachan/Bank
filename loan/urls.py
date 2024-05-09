from django.urls import path
from .views import *

urlpatterns = [
    path('loan/', DifferentLoanView.as_view(), name='loan'),
    path('loan_detail/<str:loan_name>/', LoanInterestPeriod.as_view(), name='loan_detail'),
    path('loan_apply/<int:pk>/',LoanApply.as_view(), name='loan_apply'),
    path('loan_account/',LoanAccount.as_view(), name='loan_account'),
    # path('loan_payment/',Loanpayment.as_view(), name='loan_payment'),
    path('close_loan/<str:sa>/<str:pk>/',CloseLoan.as_view(), name='close_loan'),
    path('loan_payment/<str:sa>/<str:pk>/',Loanpayment.as_view(), name='loan_payment'),


]
