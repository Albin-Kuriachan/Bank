from django.urls import path
from .views import *

urlpatterns = [
    path('fd/<int:pk>/<int:id>/', FDAccountAPIView.as_view(), name='fd'),
    path('fd_profile/', FDdetailsview.as_view(), name='fd_profile'),
    path('fd_interest_details/', FDInterestview.as_view(), name='fd_interest_details'),
    path('choose_fd_type/<int:pk>/', Choose_Fd.as_view(), name='choose_fd_type'),
    path('close_fd/<int:pk>/', Close_FD.as_view(), name='close_fd'),


]
