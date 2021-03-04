from django.core.mail import EmailMessage
import pyshorteners
from django.urls import reverse
from django.template.loader import render_to_string

class Email:
    @staticmethod
    def configureAddUserEmail(data):
        absoluteURL = "http://" + data['site'] + reverse('login') 
        email_body_template = render_to_string('registration_email_template.html', {
            'absolute_url': absoluteURL,
            'name': data['name'],
            'username': data['username'],
            'password': data['password'],
        })
        email_data = {'email_body': email_body_template, 'email_subject': 'Access Your Account', 'to_email': data['email']}
        return email_data

    @staticmethod
    def configurePasswordRestEmail(data):
        absoluteURL = "http://" + data['site'] + reverse('reset-password')+"?token="+data['token']
        shortener = pyshorteners.Shortener()
        short_url = shortener.tinyurl.short(absoluteURL)
        email_body = render_to_string('password_reset_mail_template.html', {
            'name': data['name'],
            'link': short_url
        })
        email_data = {'email_body': email_body, 'email_subject': 'Reset Your Password', 'to_email': data['email']}
        return email_data

    @staticmethod
    def configure_result_notification_mail(data):
        email_body = render_to_string('review_mail_template.html', {
            'name': data['name'],
            'marks': data['score'],
            'week_no': data['week_no'],
            'course': data['course'],
            'mentor': data['mentor'],
            'remarks': data['remark']
        })
        email_data = {'email_body': email_body, 'email_subject': 'Fellowship Review Results', 'to_email': data['email']}
        return email_data

    @staticmethod
    def sendEmail(data):
        email = EmailMessage(
            subject=data['email_subject'],
            to=(data['to_email'],)
        )
        email.attach(content=data['email_body'], mimetype='text/html')
        email.send()
