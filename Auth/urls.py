  
from django.urls import path
from . import views

urlpatterns = [
    path('register-user/', views.UserRegistrationView.as_view(), name='register-user'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangeUserPasswordView.as_view(), name='change-password'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:token>/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('change-password-on-first-access/<str:token>/', views.ChangePasswordOnFirstAccess.as_view(), name='change-password-on-first-access'),
    path('new-first-login-link-request/', views.RequestNewLoginLinkWithTokenView.as_view(), name='new-first-login-link-request'),

]