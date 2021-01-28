from .middlewares import SessionAuthentication
from django.urls import path
from . import views

urlpatterns = [
    path('add-user/', SessionAuthentication(views.UserRegistrationView.as_view()), name='add-user'),
    path('login/', views.UserLoginView.as_view(), name='login')
]

