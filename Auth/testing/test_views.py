from django.test import TestCase
from django.test import Client
from ..models import User
from django.urls import reverse
from rest_framework import status
import json


class TestAuthApp(TestCase):
    def setUp(self):
        # Admin user
        User.objects.create_user(username='birajit', password='birajit123', role='Admin',
                                 is_first_time_login=False)
        self.client = Client()

        self.valid_payload = {
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'Last',
            'email': 'birumnna@gmail.com',
            'mobile': '9915518024',
            'role': 'Engineer'
        }

        self.invalid_payload = {
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'Last',
            'email': 'birumnna@gmail.com',
            'mobile': '9915518024',
        }

    def adminLogin(self):
        self.valid_admin_credential = json.dumps({
            'username': 'birajit',
            'password': 'birajit123'
        })
        response = self.client.post(reverse('login'), data=self.valid_admin_credential, content_type='application/json')
        return response

    def logout(self):
        self.client.get(reverse('logout'))

    def test_admin_login_when_given_valid_credential(self):
        self.valid_admin_credential = json.dumps({
            'username': 'birajit',
            'password': 'birajit123'
        })
        response = self.client.post(reverse('login'), data=self.valid_admin_credential, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_admin_login_when_given_invalid_credential(self):
        self.valid_admin_credential = json.dumps({
            'username': 'birajit',
            'password': 'birajit'
        })
        response = self.client.post(reverse('login'), data=self.valid_admin_credential, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_userRegistrationAPI_when_given_valid_payload_should_return_success_response_message(self):
        self.adminLogin()
        response = self.client.post(reverse('add-user'), data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_userRegistrationAPI_when_given_invalid_payload_should_return_bad_request_response_message(self):
        self.adminLogin()
        response = self.client.post(reverse('add-user'), data=json.dumps(self.invalid_payload),
                                    content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_when_login_link_is_used_without_token_for_first_time(self):
        self.adminLogin()
        response1 = self.client.post(reverse('add-user'), data=json.dumps(self.valid_payload),
                                     content_type='application/json')
        self.logout()
        username = response1.data['username']
        password = response1.data['password']
        response = self.client.post(reverse('login'), data=json.dumps({'username': username, 'password': password}),
                                    content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_when_login_link_is_used_with_token_for_first_time(self):
        self.adminLogin()
        response1 = self.client.post(reverse('add-user'), data=json.dumps(self.valid_payload),
                                     content_type='application/json')
        self.logout()
        username = response1.data['username']
        password = response1.data['password']
        token = response1.data['token']
        response = self.client.post(f'/user/login/?token={token}', data=json.dumps({'username': username, 'password': password}),
                                    content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['response'], 'You are logged in! Now you need to change password to access resources')

    def test_user_login_when_credential_is_invalid_and_login_link_is_used_with_token_for_first_time(self):
        self.adminLogin()
        response1 = self.client.post(reverse('add-user'), data=json.dumps(self.valid_payload),
                                     content_type='application/json')
        self.logout()
        token = response1.data['token']
        response = self.client.post(f'/user/login/?token={token}', data=json.dumps({'username': 'xyzaa', 'password': 'zopaaaa'}),
                                    content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
        