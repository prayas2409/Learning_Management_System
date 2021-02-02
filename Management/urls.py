from django.urls import path
from . import views

urlpatterns = [
    path('add-course/', views.AddCourseAPIView.as_view(), name='add-course'),
    path('all-courses/', views.AllCoursesAPIView.as_view(), name='all-courses'),
    path('update-course/<int:id>', views.UpdateCourseAPIView.as_view(), name='update-course'),
    path('delete-course/<int:id>', views.DeleteCourseAPIView.as_view(), name='delete-course'),
]

