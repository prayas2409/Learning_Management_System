from django.core.mail import EmailMessage
import pyshorteners
from django.urls import reverse


class Email:
    @staticmethod
    def configureAddUserEmail(data):
        absoluteURL = "http://" + data['site'] + reverse('login') + '?token=' + data['token']
        email_body = f"Hi {data['name']}! You are added as a new {data['role']} " \
                     f"\n Please login with the following credential \n" \
                     f" Username: {data['username']}, password: {data['password']} \n" \
                     f"Link: {absoluteURL}"
        email_data = {'email_body': email_body, 'email_subject': 'Access Your Account', 'to_email': data['email']}
        return email_data

    @staticmethod
    def configurePasswordRestEmail(data):
        absoluteURL = "http://" + data['site'] + reverse('reset-password', args=[data['token']])
        shortener = pyshorteners.Shortener()
        short_url = shortener.tinyurl.short(absoluteURL)
        email_body = f"Hi {data['user'].first_name} {data['user'].last_name}! Reset your password at {data['site']}" \
                     f" with the following link \n" \
                     f"Link: {short_url}"
        email_data = {'email_body': email_body, 'email_subject': 'Reset-Password', 'to_email': data['user'].email}
        return email_data

    @staticmethod
    def configure_result_notification_mail(data):
        email_body = f"Hello {data['name']} Greetings! \n" \
                     f"Your week {data['week_no']} review results is following:\n" \
                     f"Course: {data['course']} \n" \
                     f"Mentor: {data['mentor']} \n" \
                     f"Current Score:{data['score']} \n" \
                     f"Remarks: {data['remark']} "

        email_data = {'email_body': email_body, 'email_subject': 'Fellowship Review Results', 'to_email': data['email']}
        return email_data

    @staticmethod
    def sendEmail(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=(data['to_email'],)
        )
        email.send()
