from __future__ import absolute_import, unicode_literals
from celery import shared_task
# from django_celery_results.models import TaskResult
import sys
sys.path.append("..")
from LMS.mailConfirmation import Email



# @shared_task()
# def clean_task_result_db():
#     """This function cleans the task db periodically"""
#     last_10 = TaskResult.objects.all()[:50]
#     TaskResult.objects.exclude(task_id__in=list(last_10)).delete()


@shared_task()
def send_review_result_notification_mail(data):
    """
    This function is used for sending review email to student
    """
    Email.sendEmail(Email.configure_result_notification_mail(data))
    return f"Review result notification mail is sent to {data['email']}"
