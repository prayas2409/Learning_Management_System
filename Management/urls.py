from django.urls import path
from . import views

urlpatterns = [
    path('add-course/', views.AddCourseAPIView.as_view(), name='add-course'),
    path('all-courses/', views.AllCoursesAPIView.as_view(), name='all-courses'),
]

