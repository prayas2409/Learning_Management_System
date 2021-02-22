from django.db import models
import sys
from .utils import Degree, Default

sys.path.append('..')
from Auth.models import User


def get_course_id():
    last_record = Course.objects.all().last()
    if last_record:
        str_part, int_part = last_record.cid.split('-')
        int_part = int(int_part)
        int_part += 1
        return str_part + '-' + str(int_part)
    return Default.CID.value


def get_student_id():
    last_record = Student.objects.all().last()
    if last_record:
        str_part, int_part = last_record.sid.split('-')
        int_part = int(int_part)
        int_part += 1
        return str_part + '-' + str(int_part)
    return Default.SID.value


def get_mentor_id():
    last_record = Mentor.objects.all().last()
    if last_record:
        str_part, int_part = last_record.mid.split('-')
        int_part = int(int_part)
        int_part += 1
        return str_part + '-' + str(int_part)
    return Default.MID.value


class Course(models.Model):
    """
        This model is used to create course table with below fields
    """
    course_name = models.CharField(max_length=50, unique=True)
    cid = models.CharField(max_length=10, unique=True, default=get_course_id)
    course_price = models.IntegerField(default=0)
    duration_weeks = models.IntegerField(default=0, null=True)
    description = models.CharField(max_length=150, default=None, null=True, blank=True)

    def __str__(self):
        return self.course_name


class Mentor(models.Model):
    mentor = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='mentor/', max_length=255, null=True, blank=True)
    mid = models.CharField(max_length=10, unique=True, default=get_mentor_id)
    course = models.ManyToManyField(to=Course, related_name='course_mentor')

    def __str__(self):
        return self.mentor.get_full_name()


class Student(models.Model):
    year_of_experience = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='student/', max_length=255, null=True, blank=True)
    sid = models.CharField(max_length=10, unique=True, default=get_student_id)
    alt_number = models.CharField(max_length=13, default=None, null=True, blank=True)
    relation_with_alt_number_holder = models.CharField(max_length=20, default=None, null=True, blank=True)
    current_location = models.CharField(max_length=50, default=None, null=True, blank=True)
    current_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    git_link = models.CharField(max_length=30, default=None, null=True, blank=True)
    year_of_experience = models.IntegerField(choices=year_of_experience, default=None, null=True)
    course_assigned = models.BooleanField(default=False)

    def __str__(self):
        return self.student.get_full_name()


class Education(models.Model):
    degree_choice = (
        (Degree.SSC.value, Degree.SSC.value),
        (Degree.HSC.value, Degree.HSC.value),
        (Degree.UG.value, Degree.UG.value),
        (Degree.PG.value, Degree.PG.value),

    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    institute = models.CharField(max_length=50, default=None, null=True, blank=True)
    degree = models.CharField(choices=degree_choice, max_length=10, default=None)
    stream = models.CharField(max_length=50, default=None, null=True, blank=True)
    percentage = models.FloatField(default=None, null=True, blank=True)
    from_date = models.DateField(default=None, blank=True, null=True)
    till = models.DateField(default=None, blank=True, null=True)

    def __str__(self):
        return self.student.student.get_full_name()


class StudentCourseMentor(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True)
    create_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_by')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_by')


class Performance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.FloatField(default=None, null=True)
    review_date = models.DateField(default=None, null=True)
    week_no = models.IntegerField(default=0, null=True)
    update_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='performance_update_by')
    remark = models.CharField(max_length=350, default=None, null=True)

    def __str__(self):
        return self.student.student.get_full_name()
