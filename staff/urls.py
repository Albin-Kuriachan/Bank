from django.urls import path
from .views import *

urlpatterns = [
    path('staff_register/', StaffProfileRegister.as_view(), name='staff_register'),
    # path('staff_email_verify/', UserEmailVerify.as_view(), name='staff_email_verify'),
    path('staff_login_register/', StaffLoginRegister.as_view(), name='staff_login_register'),
    path('approve_profile/', ApproveProfile.as_view(), name='approve_profile'),
    path('approve-profile/<int:profile_id>/', ApproveProfile.as_view(), name='approve_profile'),

]
