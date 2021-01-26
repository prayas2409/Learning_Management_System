from django.db import models
import sys
sys.path.append('..')
from Auth.models import User

class Course(models.Model):
    course_name = models.CharField(max_length=30)

    def __str__(self):
        return self.course_name


class Mentors(models.Model):
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ManyToManyField(to=Course, blank=True, null=True)

    def __str__(self):
        return self.mentor.get_full_name()

class Student(models.Model):
    choices = (
        (0,0),
        (1,1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    alt_number = models.CharField(max_length=13, default=None, null=True, blank=True)
    rel_of_altNo = models.CharField(max_length=20, default=None, null=True, blank=True)
    current_location = models.CharField(max_length=50, default=None, null=True, blank=True)
    current_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    git_link = models.CharField(max_length=30, default=None, null=True, blank=True)
    year_of_experience = models.IntegerField(choices=choices, default=None, null=True)

    def __str__(self):
        return self.student.get_full_name()

class Education(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    institute = models.CharField(max_length=50, default=None, null=True, blank=True)
    degree = models.CharField(max_length=50, default=None, null=True, blank=True)
    stream = models.CharField(max_length=50, default=None, null=True, blank=True)
    percentage = models.FloatField(default=None, null=True, blank=True)
    from_date = models.DateField(default=None, blank=True)
    till = models.DateField(default=None, blank=True)

    def __str__(self):
        return self.student.student.get_full_name()



class Performance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    mentor = models.ForeignKey(Mentors, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.FloatField(default=None, null=True)

    def __str__(self):
        return self.student.student.get_full_name()
