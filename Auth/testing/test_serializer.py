from django.test import TestCase
from ..models import User
from ..serializer import UserSerializer, UserLoginSerializer, ChangeUserPasswordSerializer, ForgotPasswordSerializer, \
    ResetPasswordSerializer


class AuthenticationTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'birajit123',
            'first_name': 'Birajit',
            'last_name': 'Nath',
            'email': 'birajit@gmail.com',
            'mobile': '9915518024',
            'role': 'Engineer',
        }

        self.user_test_data = {
            'username': 'birajit@',
            'first_name': 'Birajit',
            'last_name': 'Nath',
            'email': 'birajit_nath@gmail.com',
            'mobile': '9915518024',
            'role': 'Engineer',
        }

        self.user_null_data = {
            'username': '',
            'first_name': '',
            'last_name': '',
            'email': '',
            'mobile': '',
            'role': '',
        }

        self.valid_mobile_no = [
            "+919915518024", "09862361463", "7973918399", '919915518024'
        ]

        self.invalid_mobile_no = [
            "991551802475", "+551855555", "112233555", '5986231456'
        ]

        self.valid_role = ["Admin", "Engineer", "Mentor"]

        self.invalid_role = ["Doctor", 'admin', 'engineer', 'Teacher', 'mentor', 'xyz']

        self.user_login_test_data = {
            'username': 'birajit123',
            'password': '123456'
        }
        self.invalid_login_credential_format = [
            ('birajit', 'bira1'),  # not satisfying minimum password length
            ('kl', '1123332'),  # not satisfying minimum username length
            ('birajitnathdemohahahaha', '1123332'),  # not satisfying maximum username length
            ('birajit', '11233324444sshhssssssssssss')  # not satisfying maximum password length
        ]
        self.change_password_test_data = {
            'old_password': '123456',
            'new_password': 'birajit123',
            'confirm_password': 'birajit123'
        }
        self.forgot_password_test_data = {
            'email': 'birajit@gmail.com'
        }
        self.valid_email_list = ['birajit@gmail.com', 'birajit95@gmail.com', 'aryan.1.kcp@lpu.co.in']
        self.invalid_email_list = ['birajitgmial.com', 'birajit@gmail@.com', 'ak@gmail,com']

        self.reset_password_test_data = {
            'new_password': '123456',
            'confirm_password': '123456'
        }

        # saving in db
        self.user = User.objects.create(**self.user_data)
        self.user_serializer = UserSerializer(instance=self.user)
        self.user_login_serializer = UserLoginSerializer(instance=self.user_login_test_data)
        self.change_password_serializer = ChangeUserPasswordSerializer(instance=self.change_password_test_data)
        self.forgot_password_serializer = ForgotPasswordSerializer(instance=self.user)
        self.reset_password_serializer = ResetPasswordSerializer(instance=self.reset_password_test_data)

    # Test for UserSerializer

    def test_user_serializer_contains_expected_fields(self):
        self.data = self.user_serializer.data
        self.assertEquals(set(self.data.keys()), {'username', 'first_name', 'last_name', 'email', 'mobile', 'role'})

    def test_user_serializer_fields_content(self):
        self.data = self.user_serializer.data
        self.assertEquals(self.data['username'], self.user_data['username'])
        self.assertEquals(self.data['first_name'], self.user_data['first_name'])
        self.assertEquals(self.data['last_name'], self.user_data['last_name'])
        self.assertEquals(self.data['email'], self.user_data['email'])
        self.assertEquals(self.data['mobile'], self.user_data['mobile'])
        self.assertEquals(self.data['role'], self.user_data['role'])

    def test_user_serializer_when_given_empty_fields_content_should_raise_validation_error(self):
        self.serializer = UserSerializer(data=self.user_null_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors),
                          {'username', 'first_name', 'last_name', 'email', 'mobile', 'role'})

    def test_user_serializer_when_given_duplicate_username_should_raise_error(self):
        self.user_data['username'] = "birajit123"
        self.serializer = UserSerializer(data=self.user_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'username'})

    def test_user_serializer_when_given_invalid_first_name_should_return_error(self):
        self.user_test_data['first_name'] = 'birajit nath'
        self.serializer = UserSerializer(data=self.user_test_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'first_name'})

    def test_user_serializer_when_given_invalid_last_name_should_return_error(self):
        self.user_test_data['last_name'] = 'Nath Nath'
        self.serializer = UserSerializer(data=self.user_test_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'last_name'})

    def test_user_serializer_when_given_duplicate_email_should_raise_error(self):
        self.user_data['username'] = "birajit@"
        self.user_data['email'] = 'birajit@gmail.com'
        self.serializer = UserSerializer(data=self.user_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'non_field_errors'})

    def test_user_serializer_when_given_invalid_email_should_raise_error(self):
        self.user_test_data['email'] = 'birajigmail.com'
        self.serializer = UserSerializer(data=self.user_test_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'email'})

    def test_user_serializer_when_given_valid_mobile_no_should_return_true(self):
        for valid_mobile_no in self.valid_mobile_no:
            self.user_test_data['mobile'] = valid_mobile_no
            self.serializer = UserSerializer(data=self.user_test_data)
            self.assertTrue(self.serializer.is_valid())

    def test_user_serializer_when_given_invalid_mobile_no_should_raise_error(self):
        for invalid_mobile_no in self.invalid_mobile_no:
            self.user_test_data['mobile'] = invalid_mobile_no
            self.serializer = UserSerializer(data=self.user_test_data)
            self.assertFalse(self.serializer.is_valid())
            self.assertEquals(set(self.serializer.errors), {'mobile'})

    def test_user_serializer_when_given_valid_role_should_return_true(self):
        for valid_role in self.valid_role:
            self.user_test_data['role'] = valid_role
            self.serializer = UserSerializer(data=self.user_test_data)
            self.assertTrue(self.serializer.is_valid())

    def test_user_serializer_when_given_invalid_role_should_return_true(self):
        for invalid_role in self.invalid_role:
            self.user_test_data['role'] = invalid_role
            self.serializer = UserSerializer(data=self.user_test_data)
            self.assertFalse(self.serializer.is_valid())
            self.assertEquals(set(self.serializer.errors), {'role'})

    # user login serializer tests

    def test_login_serializer_contains_expected_fields(self):
        data = self.user_login_serializer.data
        self.assertCountEqual(set(data.keys()), {'username', 'password'})

    def test_login_serializer_fields_content(self):
        data = self.user_login_serializer.data
        self.assertEqual(data['username'], self.user_login_test_data['username'])
        self.assertEqual(data['password'], self.user_login_test_data['password'])

    def test_user_login_serializer_when_given_invalid_login_credential_format_return_True(self):
        for username, password in self.invalid_login_credential_format:
            self.user_login_test_data['username'] = username
            self.user_login_test_data['password'] = password
            self.serializer = UserLoginSerializer(data=self.user_login_test_data)
            self.assertFalse(self.serializer.is_valid())

    # Test cases for Chnage password serializer

    def test_change_password_serializer_contains_expected_fields(self):
        data = self.change_password_serializer.data
        self.assertCountEqual(set(data.keys()), {'old_password', 'new_password', 'confirm_password'})

    def test_change_password_serializer_fields_content(self):
        data = self.change_password_serializer.data
        self.assertEqual(data['old_password'], self.change_password_test_data['old_password'])
        self.assertEqual(data['new_password'], self.change_password_test_data['new_password'])
        self.assertEqual(data['confirm_password'], self.change_password_test_data['confirm_password'])

    def test_when_given_miss_matched_new_and_confirm_passwords_should_raise_error(self):
        self.change_password_test_data['new_password'] = '123456'
        self.change_password_test_data['confirm_password'] = 'birajit12'
        self.serializer = ChangeUserPasswordSerializer(data=self.change_password_test_data)
        self.assertFalse(self.serializer.is_valid())

    def test_when_given_new_password_and_confirm_password_length_bellow_6_chars_should_raise_error(self):
        self.change_password_test_data['new_password'] = '12345'
        self.change_password_test_data['confirm_password'] = '12345'
        self.serializer = ChangeUserPasswordSerializer(data=self.change_password_test_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'new_password', 'confirm_password'})

    def test_when_given_new_password_and_confirm_password_length_above_20_chars_should_raise_error(self):
        self.change_password_test_data['new_password'] = '12345shshshhsqhqsqs55qs5s5q5s5s5'
        self.change_password_test_data['confirm_password'] = '12345shshshhsqhqsqs55qs5s5q5s5s5'
        self.serializer = ChangeUserPasswordSerializer(data=self.change_password_test_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'new_password', 'confirm_password'})

    # Test cases for forgot password serializer

    def test_forgot_password_serializer_when_given_invalid_mail_should_return_True(self):
        for invalid_email in self.invalid_email_list:
            self.forgot_password_test_data['email'] = invalid_email
            self.serializer = ForgotPasswordSerializer(data=self.forgot_password_test_data)
            self.assertFalse(self.serializer.is_valid())
            self.assertEquals(set(self.serializer.errors), {'email'})

    def test_forgot_password_serializer_when_given_valid_mail_should_return_True(self):
        for valid_email in self.valid_email_list:
            self.forgot_password_test_data['email'] = valid_email
            self.serializer = ForgotPasswordSerializer(data=self.forgot_password_test_data)
            self.assertTrue(self.serializer.is_valid())

    # Test cases for reset password serializer

    def test_reset_password_serializer_when_given_matching_new_and_confirm_password_should_return_True(self):
        self.serializer = ResetPasswordSerializer(data=self.reset_password_test_data)
        self.assertTrue(self.serializer.is_valid())

    def test_reset_password_serializer_when_given_miss_matching_new_and_confirm_password_should_return_False(self):
        self.reset_password_test_data['new_password'] = '123456'
        self.reset_password_test_data['confirm_password'] = 'abcdef'
        self.serializer = ResetPasswordSerializer(data=self.reset_password_test_data)
        self.assertFalse(self.serializer.is_valid())

    def test_reset_password_serializer_when_given_new_password_and_confirm_password_length_above_20_chars_should_raise_error(self):
        self.reset_password_test_data['new_password'] = '12345shshshhsqhqsqs55qs5s5q5s5s5'
        self.reset_password_test_data['confirm_password'] = '12345shshshhsqhqsqs55qs5s5q5s5s5'
        self.serializer = ResetPasswordSerializer(data=self.reset_password_test_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'new_password', 'confirm_password'})

    def test_reset_password_serializer_when_given_new_password_and_confirm_password_length_bellow_6_chars_should_raise_error(self):
        self.reset_password_test_data['new_password'] = '12345'
        self.reset_password_test_data['confirm_password'] = '12345'
        self.serializer = ResetPasswordSerializer(data=self.reset_password_test_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'new_password', 'confirm_password'})


