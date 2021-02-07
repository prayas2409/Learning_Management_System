from django.test import TestCase
from ..models import User
from ..serializers import UserSerializer


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

        # saving in db
        self.user = User.objects.create(**self.user_data)
        self.user_serializer = UserSerializer(instance=self.user)

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
        self.assertEquals(set(self.serializer.errors), {'username', 'first_name', 'last_name', 'email', 'mobile', 'role'})

    def test_when_given_duplicate_username_should_raise_error(self):
        self.user_data['username'] = "birajit123"
        self.serializer = UserSerializer(data=self.user_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'username'})

    def test_when_given_invalid_first_name_should_return_error(self):
        self.user_test_data['first_name'] = 'birajit nath'
        self.serializer = UserSerializer(data=self.user_test_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'first_name'})

    def test_when_given_invalid_last_name_should_return_error(self):
        self.user_test_data['last_name'] = 'Nath Nath'
        self.serializer = UserSerializer(data=self.user_test_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'last_name'})

    def test_when_given_duplicate_email_should_raise_error(self):
        self.user_data['username'] = "birajit@"
        self.user_data['email'] = 'birajit@gmail.com'
        self.serializer = UserSerializer(data=self.user_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'non_field_errors'})

    def test_when_given_invalid_email_should_raise_error(self):
        self.user_test_data['email'] = 'birajigmail.com'
        self.serializer = UserSerializer(data=self.user_test_data)
        self.assertFalse(self.serializer.is_valid())
        self.assertEquals(set(self.serializer.errors), {'email'})

    def test_when_given_valid_mobile_no_should_return_true(self):
        for valid_mobile_no in self.valid_mobile_no:
            self.user_test_data['mobile'] = valid_mobile_no
            self.serializer = UserSerializer(data=self.user_test_data)
            self.assertTrue(self.serializer.is_valid())

    def test_when_given_invalid_mobile_no_should_raise_error(self):
        for invalid_mobile_no in self.invalid_mobile_no:
            self.user_test_data['mobile'] = invalid_mobile_no
            self.serializer = UserSerializer(data=self.user_test_data)
            self.assertFalse(self.serializer.is_valid())
            self.assertEquals(set(self.serializer.errors), {'mobile'})

    def test_when_given_valid_role_should_return_true(self):
        for valid_role in self.valid_role:
            self.user_test_data['role'] = valid_role
            self.serializer = UserSerializer(data=self.user_test_data)
            self.assertTrue(self.serializer.is_valid())

    def test_when_given_invalid_role_should_return_true(self):
        for invalid_role in self.invalid_role:
            self.user_test_data['role'] = invalid_role
            self.serializer = UserSerializer(data=self.user_test_data)
            self.assertFalse(self.serializer.is_valid())
            self.assertEquals(set(self.serializer.errors), {'role'})

