
from django.urls import path
from .views import *

urlpatterns = [
    path('', UserProfileRegister.as_view(), name='user-register'),
    path('updateprofile/<int:pk>/', UpdateProfileApi.as_view(), name='updateprofile'),
    path('userprofiledata/', UserProfile.as_view(), name='userprofiledata'),
    # path('userprofiledata/<int:pk>/', UserProfile.as_view(), name='userprofiledata'),
    path('profile_display/', ProfileDisplayView.as_view(), name='profile_display'),
    path('login/', LoginView.as_view(), name='login'),

]