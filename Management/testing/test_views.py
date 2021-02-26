from django.test import TestCase
from django.test import Client
from ..models import User, Course, Mentor
from django.urls import reverse
from rest_framework import status
import json

from ..serializer import CourseMentorSerializer


class TestManagementApp(TestCase):
    def setUp(self):
        # Admin user
        User.objects.create_user(username='ranjith', password='ranjith123', role='Admin',
                                 is_first_time_login=False)
        # Engineer user
        User.objects.create_user(username='RahulKL', password='rahul123', role='Engineer',
                                 is_first_time_login=False)
        # Mentor user
        self.Mentor = User.objects.create_user(username='Shreyas', password='Shreyas', role='Mentor',
                                               is_first_time_login=False)

        self.client = Client()

        self.valid_payload = {
            'course_name': 'Python',
            'duration_weeks': '6',
            'description': 'Python desk',
            'course_price': '12000'
        }

        self.invalid_payload = {
            'course_name': '',
            'duration_weeks': 'one',
            'description': 'Python desk',
            'course_price': '12000'
        }

        self.course = Course.objects.create(course_name='Java', duration_weeks='6', description='Python desk',
                                            course_price='12000')

        self.mentor_course = Mentor.objects.get(mentor=self.Mentor)

        # Assign course to mentor-course object
        self.mentor_course.course.add(self.course)
        self.mentor_course.save()

    ### Test cases for Add Course API

    def test_add_course_api_after_login_with_valid_credentials(self):
        self.valid_admin_credential = json.dumps({
            'username': 'ranjith',
            'password': 'ranjith123'
        })
        login = self.client.post(reverse('login'), data=self.valid_admin_credential, content_type='application/json')
        token = login['Authorization']
        auth_headers = {
            'HTTP_AUTHORIZATION': token,
        }
        response = self.client.post(reverse('add-course'), **auth_headers, data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_course_api_without_login_with_valid_credentials(self):
        response = self.client.post(reverse('add-course'), data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_course_api_after_login_with_invalid_payload(self):
        self.valid_admin_credential = json.dumps({
            'username': 'ranjith',
            'password': 'ranjith123'
        })
        login = self.client.post(reverse('login'), data=self.valid_admin_credential, content_type='application/json')
        token = login['Authorization']
        auth_headers = {
            'HTTP_AUTHORIZATION': token,
        }
        response = self.client.post(reverse('add-course'), **auth_headers, data=json.dumps(self.invalid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_course_api_after_login_with_invalid_login_credentials(self):
        self.invalid_admin_credential = json.dumps({
            'username': 'hello',
            'password': '321'
        })
        login = self.client.post(reverse('login'), data=self.invalid_admin_credential, content_type='application/json')
        self.assertEqual(login.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_course_api_after_login_with_valid_credentials_role_student(self):
        self.valid_admin_credential = json.dumps({
            'username': 'RahulKL',
            'password': 'rahul123'
        })
        login = self.client.post(reverse('login'), data=self.valid_admin_credential, content_type='application/json')
        token = login['Authorization']
        auth_headers = {
            'HTTP_AUTHORIZATION': token,
        }
        response = self.client.post(reverse('add-course'), **auth_headers, data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_course_api_after_login_with_valid_credentials_role_mentor(self):
        self.valid_admin_credential = json.dumps({
            'username': 'Shreyas',
            'password': 'Shreyas'
        })
        login = self.client.post(reverse('login'), data=self.valid_admin_credential, content_type='application/json')
        token = login['Authorization']
        auth_headers = {
            'HTTP_AUTHORIZATION': token,
        }
        response = self.client.post(reverse('add-course'), **auth_headers, data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    ### Test Cases for MentorStudentCourse API

    def test_Listing_students_with_mentorid_courseid_api_without_login_without_alloting_course_to_mentor(self):
        response = self.client.get(
            reverse('mentor-student-course', kwargs={'mentor_id': self.Mentor.id, 'course_id': self.course.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_Listing_students_with_mentorid_courseid_api_after_login_without_alloting_course_to_mentor(self):
        self.valid_admin_credential = json.dumps({
            'username': 'ranjith',
            'password': 'ranjith123'
        })
        login = self.client.post(reverse('login'), data=self.valid_admin_credential, content_type='application/json')
        token = login['Authorization']
        auth_headers = {
            'HTTP_AUTHORIZATION': token,
        }
        response = self.client.get(
            reverse('mentor-student-course', kwargs={'mentor_id': self.Mentor.id, 'course_id': self.course.id}),
            **auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_Listing_students_with_mentorid_courseid_api_after_login(self):
        self.valid_admin_credential = json.dumps({
            'username': 'ranjith',
            'password': 'ranjith123'
        })
        login = self.client.post(reverse('login'), data=self.valid_admin_credential, content_type='application/json')
        token = login['Authorization']
        auth_headers = {
            'HTTP_AUTHORIZATION': token,
        }
        response = self.client.get(
            reverse('mentor-student-course', kwargs={'mentor_id': self.mentor_course.id, 'course_id': self.course.id}),
            **auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



    ### Test cases for MentorDetailsAPI

