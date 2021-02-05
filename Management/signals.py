from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Student, Mentor, Education
import sys
sys.path.append('..')
from Auth.models import User
from Auth.permissions import Role

@receiver(signal=post_save, sender=User)
def create_student_or_mentor(sender, instance, created, **kwargs):
    if created:
        if instance.role == Role.STUDENT.value:
            student = Student.objects.create(student=instance)
            Education.objects.create(student=student)
        elif instance.role == Role.MENTOR.value:
            Mentor.objects.create(mentor=instance)



