from django.urls import path
from . import views

urlpatterns = [
    path('add-user/', views.UserRegistrationView.as_view(), name='add-user'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangeUserPasswordView.as_view(), name='change-password'),

]

