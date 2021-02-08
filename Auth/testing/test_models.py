from django.test import TestCase
from ..models import User
import sys
sys.path.append('..')
from Management.models import Mentor, Student


class AuthModels(TestCase):

    def setUp(self):
        self.student = User.objects.create(username='student', first_name='Student', last_name='Student',
                                           email='student@gmail.com', mobile='9915518024', password='123456', role='Engineer')
        self.admin = User.objects.create(username='admin', first_name='Admin', last_name='Admin',
                                         email='admin@gmail.com', mobile='9915518025', password='123456', role='Admin')
        self.mentor = User.objects.create(username='mentor', first_name='Mentor', last_name='Mentor',
                                          email='mentor@gmail.com', mobile='9915518026', password='123456', role='Mentor')

    def test_admin_creation(self):
        user = User.objects.get(username='admin')
        self.assertEqual(user.email, 'admin@gmail.com')
        self.assertEqual(user.first_name, 'Admin')
        self.assertEqual(user.last_name, 'Admin')
        self.assertEqual(user.mobile, '9915518025')
        self.assertEqual(user.role, 'Admin')
        self.assertEqual(user.get_full_name(), "Admin Admin")

    def test_mentor_creation(self):
        user = User.objects.get(username='mentor')
        self.assertEqual(user.email, 'mentor@gmail.com')
        self.assertEqual(user.first_name, 'Mentor')
        self.assertEqual(user.last_name, 'Mentor')
        self.assertEqual(user.mobile, '9915518026')
        self.assertEqual(user.role, 'Mentor')
        self.assertEqual(user.get_full_name(), "Mentor Mentor")

        # When mentor is created that time along with user Mentor table should also be created
        mentor = Mentor.objects.get(mentor_id=user.id)
        self.assertTrue(mentor)

    def test_Student_creation(self):
        user = User.objects.get(username='student')
        self.assertEqual(user.email, 'student@gmail.com')
        self.assertEqual(user.first_name, 'Student')
        self.assertEqual(user.last_name, 'Student')
        self.assertEqual(user.mobile, '9915518024')
        self.assertEqual(user.role, 'Engineer')
        self.assertEqual(user.get_full_name(), "Student Student")

        # When student is created that time along with user Student table should also be created
        student = Student.objects.get(student_id=user.id)
        self.assertTrue(student)

