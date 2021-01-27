from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Student, Mentor
import sys
sys.path.append('..')
from Auth.models import User

@receiver(signal=post_save, sender=User)
def create_student_or_mentor(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'Engineer':
            Student.objects.create(student=instance)
        elif instance.role == 'Mentor':
            Mentor.objects.create(mentor=instance)



