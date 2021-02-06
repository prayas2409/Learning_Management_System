from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Student, Mentor, Education, StudentCourseMentor, Performance

import sys
sys.path.append('..')
from Auth.models import User
from Auth.permissions import Role


@receiver(signal=post_save, sender=User)
def create_student_or_mentor(sender, instance, created, **kwargs):
    if created:
        if instance.role == Role.STUDENT.value:
            Student.objects.create(student=instance)
        elif instance.role == Role.MENTOR.value:
            Mentor.objects.create(mentor=instance)


@receiver(signal=post_save, sender=StudentCourseMentor)
def create_performace_record(sender, instance, created, **kwargs):
    if created:
        for week_no in range(1, instance.course.duration_weeks+1):
            Performance.objects.create(student=instance.student, mentor=instance.mentor,
                                       course=instance.course, week_no=week_no)
