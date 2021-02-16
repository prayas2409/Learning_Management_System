from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import User
from Management.models import Mentor, Student, Course, StudentCourseMentor
from ..serializers import AddStudentSerializer, MentorCourseSerializer
import json
from rest_framework.response import Response
import datetime

CONTENT_TYPE = 'application/json'


class ManagementAPITest(TestCase):
    """ Test module for authentication APIs """

    def setUp(self):
        # initialize the APIClient app
        self.client = Client()

        self.admin = User.objects.create_user(username='admin', first_name='Bharti', last_name='Mali', role='Admin',
                                              email='admin@gmail.com', password='bharti',
                                              last_login='2021-02-12 03:56:22.00794+05:30')
        self.student = User.objects.create_user(username='student', first_name='Bharti', last_name='Mali',
                                                role='Engineer', email='student@gmail.com', password='bharti',
                                                last_login=str(datetime.datetime.now()))
        self.mentor = User.objects.create_user(username='mentor', first_name='Bharti', last_name='Mali', role='Mentor',
                                               email='mentor@gmail.com', password='bharti',
                                               last_login=str(datetime.datetime.now()))

        # Create course model object
        self.course1 = Course.objects.create(course_name='Python')
        self.course2 = Course.objects.create(course_name='Java')
        self.course3 = Course.objects.create(course_name='Django')

        # Create student model object
        self.student_details = Student.objects.get(student=self.student)

        # Create mentor-course object
        self.mentor_course = Mentor.objects.get(mentor=self.mentor)

        # Assign course to mentor-course object
        self.mentor_course.course.add(self.course1)
        self.mentor_course.save()

        self.valid_add_student_payload = {
            "name": "Bharti Mali",
            "email": "user@example.com",
            "mobile": "8787878787",
            "student": {
                "course": self.course1.id,
                "mentor": self.mentor_course.id
            }
        }

        self.invalid_add_student_payload = {
            "name": "Bharti Mali",
            "email": "user@example.com",
            "mobile": "8787878787",
            "student": {
                "course": self.course2.id,
                "mentor": self.mentor_course.id
            }
        }
        self.admin_login_payload = {
            'username': 'admin',
            'password': 'bharti'
        }
        self.mentor_login_payload = {
            'username': 'mentor',
            'password': 'bharti'
        }
        self.student_login_payload = {
            'username': 'student',
            'password': 'bharti'
        }
        self.invalid_login_payload = {
            'username': 'bharti',
            'password': 'bharti'
        }
        self.valid_mentor_payload = {
            "name": "Mentor",
            "email": "mentor@example.com",
            "mobile": "7418529630",
            "mentor": {
                "course": [
                    self.course1.id
                ]
            }
        }
        self.invalid_mentor_payload = {
            "name": " ",
            "email": "mentor@example.com",
            "mobile": "7418529630",
            "mentor": {
                "course": [
                    self.course1.id
                ]
            }
        }

    ### Test cases for AddStudent API :

    def login_method(self, credentials):
        login = self.client.post(reverse('login'), data=json.dumps(credentials), content_type=CONTENT_TYPE)
        token = login.get('authorization')
        auth_headers = {
            'HTTP_AUTHORIZATION': token,
        }
        return auth_headers

    def test_add_student_with_valid_payload_without_login(self):
        response = self.client.post(reverse('student'), data=json.dumps(self.valid_add_student_payload),
                                    content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_student_with_valid_payload_after_login_by_invalid_credentials(self):
        auth_headers = self.login_method(self.invalid_login_payload)
        response = self.client.post(reverse('student'), **auth_headers, data=json.dumps(self.valid_add_student_payload), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_student_with_valid_payload_after_login_by_admin_credentials(self):
        auth_headers = self.login_method(self.admin_login_payload)
        response = self.client.post(reverse('student'), **auth_headers, data=json.dumps(self.valid_add_student_payload), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_student_with_invalid_payload_after_login_by_admin_credentials(self):
        auth_headers = self.login_method(self.admin_login_payload)
        response = self.client.post(reverse('student'), **auth_headers,
                                    data=json.dumps(self.invalid_add_student_payload), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_student_with_valid_payload_after_login_by_mentor_credentials(self):
        auth_headers = self.login_method(self.mentor_login_payload)
        response = self.client.post(reverse('student'), **auth_headers,
                                    data=json.dumps(self.valid_add_student_payload), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_student_with_valid_payload_after_login_by_student_credentials(self):
        auth_headers = self.login_method(self.student_login_payload)
        response = self.client.post(reverse('student'), **auth_headers,
                                    data=json.dumps(self.valid_add_student_payload), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test cases for Add Mentor
    def test_add_mentor_with_valid_payload_without_login(self):
        """This test case is for testing the add mentor API without admin login"""
        response = self.client.post(reverse('mentor'), data=json.dumps(self.valid_mentor_payload),
                                    content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_mentor_with_valid_payload_after_login_by_admin_credentials(self):
        """This test case is for testing the add mentor API with admin login"""
        auth_headers = self.login_method(self.admin_login_payload)
        response = self.client.post(reverse('mentor'), **auth_headers,
                                    data=json.dumps(self.valid_mentor_payload), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_mentor_with_invalid_payload_after_login_by_admin_credentials(self):
        """This test case is for testing the add mentor API with invalid mentor payload with admin login"""
        auth_headers = self.login_method(self.admin_login_payload)
        response = self.client.post(reverse('mentor'), **auth_headers,
                                    data=json.dumps(self.invalid_mentor_payload), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_mentor_with_valid_payload_after_login_by_mentor_credentials(self):
        """This test case is for testing the add mentor API with mentor login credentials"""
        auth_headers = self.login_method(self.mentor_login_payload)
        response = self.client.post(reverse('mentor'), **auth_headers,
                                    data=json.dumps(self.valid_mentor_payload), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


### Test cases for GetMentorDetails API :
    def test_get_mentor_details_with_valid_payload_without_login(self):
        response = self.client.get(reverse('mentordetails'), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_mentor_details_with_valid_payload_after_login_by_invalid_credentials(self):
        auth_headers = self.login_method(self.invalid_login_payload)
        response = self.client.get(reverse('mentordetails'), **auth_headers, content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_mentor_details_with_valid_payload_after_login_by_admin_credentials(self):
        auth_headers = self.login_method(self.admin_login_payload)
        response = self.client.get(reverse('mentordetails'), **auth_headers, content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_mentor_details_with_valid_payload_after_login_by_mentor_credentials(self):
        auth_headers = self.login_method(self.mentor_login_payload)
        response = self.client.get(reverse('mentordetails'), **auth_headers, content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_mentor_details_with_valid_payload_after_login_by_student_credentials(self):
        auth_headers = self.login_method(self.student_login_payload)
        response = self.client.get(reverse('mentordetails'), **auth_headers, content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    