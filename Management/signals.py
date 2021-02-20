from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Student, Mentor, StudentCourseMentor, Performance, Education
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


@receiver(signal=post_save, sender=StudentCourseMentor)
def create_performace_record(sender, instance, created, **kwargs):
    if not created:
        old_records = Performance.objects.filter(student_id=instance.student.id, score=None)
        for record in old_records:
            record.delete()
    for week_no in range(1, instance.course.duration_weeks+1):
        Performance.objects.create(student=instance.student, mentor=instance.mentor,
                                    course=instance.course, week_no=week_no)


@receiver(signal=post_save, sender=Performance)
def notify_student_about_review_result(sender, instance, created, **kwargs):
    if not created:
        data = {
            'name': instance.student.student.get_full_name(),
            'email': instance.student.student.email,
            'week_no': instance.week_no,
            'score': instance.score,
            'course': instance.course.course_name,
            'mentor': instance.mentor.mentor.get_full_name(),
            'remark': instance.remark
        }
        send_review_result_notification_mail.delay(data)
