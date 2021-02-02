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
            'role': 'Admin'
        }
        self.valid_normal_user_payload = {
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
        self.new_password = 'birajit123'

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
        return response

    def test_user_login_when_credential_is_invalid_and_login_link_is_used_with_token_for_first_time(self):
        self.adminLogin()
        response1 = self.client.post(reverse('add-user'), data=json.dumps(self.valid_payload),
                                     content_type='application/json')
        self.logout()
        token = response1.data['token']
        response = self.client.post(f'/user/login/?token={token}', data=json.dumps({'username': 'xyzaa', 'password': 'zopaaaa'}),
                                    content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_after_first_login_using_the_token_sent_on_mail(self):
        login_response = self.test_user_login_when_login_link_is_used_with_token_for_first_time()
        data = json.dumps({
            'new_password':self.new_password,
            'confirm_password':self.new_password
        })
        response = self.client.put(login_response.data['link'], data=data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_cant_access_other_resorce_before_changing_password(self):
        self.test_user_login_when_login_link_is_used_with_token_for_first_time()
        response = self.client.get(reverse('add-user'))
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_access_resorcess_after_changing_password_on_first_login(self):
        self.test_change_password_after_first_login_using_the_token_sent_on_mail()
        data = json.dumps({
            'username': 'test_user',
            'password': self.new_password
        })
        self.client.post(reverse('login'), data=data, content_type='application/json')
        response = self.client.get(reverse('add-user'))
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)

    def test_when_logged_in_with_non_admin_user_cant_access_admin_resorce(self):
        User.objects.create_user(username='test_user', password='123456', role='Engineer', mobile='9915518025')
        self.client.post(reverse('login'), data=json.dumps({'username': 'test_user', 'password': '123456'}),
                         content_type='application/json')
        response = self.client.get(reverse('add-user'))
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forgot_password_when_given_mail_is_present_in_DB_and_user_is_not_logged_in(self):
        user = User.objects.create_user(username='test_user', password='123456',
                                        email='birajit95@gmail.com', mobile='9915518024')
        valid_data = json.dumps({
            'email': user.email
        })
        response = self.client.post(reverse('forgot-password'), data=valid_data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_forgot_password_when_given_mail_is_not_present_in_DB_and_user_is_not_logged_in(self):
        User.objects.create_user(username='test_user', password='123456',
                                        email='birajit95@gmail.com', mobile='9915518024')
        valid_data = json.dumps({
            'email': 'xyz@gmail.com'
        })
        response = self.client.post(reverse('forgot-password'), data=valid_data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_forgot_password_when_given_invalid_mail_id_and_user_is_not_logged_in(self):
        invalid_data = json.dumps({
            'email': 'xyzgmail.com'
        })
        response = self.client.post(reverse('forgot-password'), data=invalid_data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_forgot_password_when_user_is_logged_in(self):
        self.adminLogin()
        valid_data = json.dumps({
            'email': 'birajit@gmail.com'
        })
        response = self.client.post(reverse('forgot-password'), data=valid_data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)