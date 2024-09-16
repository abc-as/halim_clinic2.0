from django.urls import path
from .views import (register, verify_otp, login_view,verify_otp_login,ProfileView,
                    EditProfileView,CreateProfileView, HomeView, logout_user, about
                    )


urlpatterns = [
    path('register/', register, name='register'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('verify_otp_login/', verify_otp_login, name='verify_otp_login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('profile/create/', CreateProfileView.as_view(), name='create_profile'),
    path('', HomeView, name='dashboard'),
    path('logout/', logout_user, name='logout'),
    path('about/', about, name='about'),
]

