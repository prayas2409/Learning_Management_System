from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Student, Mentor, Education
import sys
sys.path.append('..')
from Auth.models import User

@receiver(signal=post_save, sender=User)
def create_student_or_mentor(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'Engineer':
            student = Student.objects.create(student=instance)
            Education.objects.create(student=student)
        elif instance.role == 'Mentor':
            Mentor.objects.create(mentor=instance)



