from django.urls import path
from . import views

urlpatterns = [
    path('add-course/', views.AddCourseAPIView.as_view(), name='add-course'),
    path('all-courses/', views.AllCoursesAPIView.as_view(), name='all-courses'),
    path('update-course/<int:course_id>/', views.UpdateCourseAPIView.as_view(), name='update-course'),
    path('delete-course/<int:id>/', views.DeleteCourseAPIView.as_view(), name='delete-course'),
    path('course-mentor/<int:mentor_id>/', views.CourseToMentorMapAPIView.as_view(), name='course-mentor'),
    path('course-mentor/<int:mentor_id>/<int:course_id>/', views.DeleteCourseFromMentorListAPIView.as_view(),
         name='delete-mentor-course'),
    path('mentors/', views.AllMentorDetailsAPIView.as_view(), name='mentors'),
    path('mentors/<int:mentor_id>/', views.MentorDetailsAPIView.as_view(), name='mentor'),
    path('student-course-mentor/', views.StudentCourseMentorMapAPIView.as_view(), name='student-course-mentor'),
    path('student-course-mentor/<int:student_id>/', views.StudentCourseMentorUpdateAPIView.as_view(),
         name='student-course-mentor-update'),
    path('get-mentors-for-course/<course_id>/', views.GetMentorsForSpecificCourse.as_view(),
         name='get-mentors-for-course'),
    path('students/', views.StudentsAPIView.as_view(), name='student'),
    path('students/basic-details/<int:student_id>', views.StudentDetailsAPIView.as_view(), name='student-details'),
    path('students/education-details/<int:student_id>', views.EducationDetails.as_view(), name='education-details'),
    path('students/basic-details/update/', views.StudentsDetailsUpdateAPIView.as_view(), name='basic-details-update'),
    path('students/education-details/update/<int:record_id>', views.EducationDetailsUpdate.as_view(), name='education-details-update'),
    path('students/education-details/add/', views.EducationDetailsAdd().as_view(), name='education-details-add'),
    path('students/new-students/', views.NewStudents.as_view(), name='new-students'),
    path('students/performance/<int:student_id>/', views.StudentPerformance.as_view(), name='student-performance'),
    path('students/performance/update/<int:student_id>/<int:week_no>', views.StudentPerfromanceUpdate.as_view(),
          name='performance-update'),
    
    path('students/performance/update-file', views.UpdateScoreFromExcel.as_view(), name='update-file'),
]

