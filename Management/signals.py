from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Student, Mentor, StudentCourseMentor, Performance
from .tasks import send_review_result_notification_mail

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




@receiver(signal=post_save, sender=Performance)
def notify_student_about_review_result(sender, instance, created, **kwargs):
    data = {
            'name': instance.student.student.get_full_name(),
            'email': instance.student.student.email,
            'week_no': instance.week_no,
            'score': instance.score,
            'course': instance.course.course_name,
            'mentor': instance.mentor.mentor.get_full_name(),
            'remark': instance.remark,
            'is_update': False
        }
    if not created:
        data['is_update'] = True
    send_review_result_notification_mail.delay(data)
