from django.test import TestCase
from ..models import Course
from ..serializers import CourseSerializer

class AuthenticationTest(TestCase):
    def setUp(self):
        self.course_data = {
            'course_name': 'Python',
            'duration_weeks': 5
        }
        self.course_test_data = {
            'course_name': 'Java',
            'duration_weeks': 6
        }

        # db initializations
        course = Course.objects.create(**self.course_data)
        self.course_serializer = CourseSerializer(instance=course)

    # Test cases for course serializer
    def test_course_serializer_when_given_valid_data_should_return_True(self):
        self.serializer = CourseSerializer(data=self.course_test_data)
        self.assertTrue(self.serializer.is_valid())

    def test_course_serializer_when_given_invalid_data_should_return_False(self):
        self.course_test_data['course_name'] = ""
        self.course_test_data['duration_weeks'] = ""
        self.serializer = CourseSerializer(data=self.course_test_data)
        self.assertFalse(self.serializer.is_valid())

    def test_course_serializer_when_given_valid_data_should_return_upper_case_course_name(self):
        self.serializer = CourseSerializer(data=self.course_test_data)
        self.assertTrue(self.serializer.is_valid())
        self.assertEqual(self.serializer.data.get('course_name'), 'JAVA')

    def test_course_serializer_in_read_mode_should_return_expected_data(self):
        self.data = self.course_serializer.data
        self.assertEqual(set(self.data), {'id', 'duration_weeks', 'course_name'})



