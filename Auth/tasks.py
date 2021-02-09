from __future__ import absolute_import, unicode_literals
from celery import shared_task
import sys
sys.path.append("..")
from LMS.mailConfirmation import Email


@shared_task()
def send_registration_mail(data):
    Email.sendEmail(Email.configureAddUserEmail(data))
    return f"Registration confirmation mail is sent {data['email']}"


@shared_task()
def send_password_reset_mail(data):
    Email.sendEmail(Email.configurePasswordRestEmail(data))
    return f"Password reset mail is sent"

