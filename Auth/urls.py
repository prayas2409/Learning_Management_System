
from django.urls import path
from . import views

urlpatterns = [
    path('add-user/', views.UserRegistrationView.as_view(), name='add-user')
]

