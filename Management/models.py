from django.db import models
import sys

sys.path.append('..')
from Auth.models import User


class Course(models.Model):
    course_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        # return self.course_name
        return str({
            'id': self.id,
            'name': self.course_name
        })

    def __json__(self):
        return {
            'id': self.id,
            'name': self.course_name
        }


class Mentor(models.Model):
    mentor = models.OneToOneField(User, on_delete=models.CASCADE)
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
    alt_number = models.CharField(max_length=13, default=None, null=True, blank=True)
    relation_with_alt_number_holder = models.CharField(max_length=20, default=None, null=True, blank=True)
    current_location = models.CharField(max_length=50, default=None, null=True, blank=True)
    current_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    git_link = models.CharField(max_length=30, default=None, null=True, blank=True)
    year_of_experience = models.IntegerField(choices=year_of_experience, default=None, null=True)

    def __str__(self):
        return self.student.get_full_name()


class Education(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    institute = models.CharField(max_length=50, default=None, null=True, blank=True)
    degree = models.CharField(max_length=50, default=None, null=True, blank=True)
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
    review_date = models.DateField(default=None)
    score = models.FloatField()

    def __str__(self):
        return self.student.student.get_full_name()
