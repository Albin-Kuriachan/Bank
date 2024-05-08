
from django.urls import path
from .views import *

urlpatterns = [
    path('user_register/', UserProfileRegister.as_view(), name='user_register'),
    path('user_email_verify/', UserEmailVerify.as_view(), name='user_email_verify'),
    path('updateprofile/<int:pk>/', UpdateProfileApi.as_view(), name='updateprofile'),
    path('userprofiledata/', UserProfile.as_view(), name='userprofiledata'),
    # path('userprofiledata/<int:pk>/', UserProfile.as_view(), name='userprofiledata'),
    path('profile_display/', ProfileDisplayView.as_view(), name='profile_display'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('login_register/', LoginRegister.as_view(), name='login_register'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),

]