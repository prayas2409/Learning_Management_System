from django.core.mail import EmailMessage


class Email:
    @staticmethod
    def configureAddUserEmail(data):
        absoluteURL = "http://"+data['site']+'/'+'user/login/'
        email_body = f"Hi {data['name']}! You are added as a new {data['role']} " \
                     f"\n Please login with the following credential \n" \
                     f" Username: {data['username']}, password: {data['password']} \n" \
                     f"Link: {absoluteURL}"
        email_data = {'email_body': email_body, 'email_subject': 'Access Your Account', 'to_email': data['email']}
        return email_data

    @staticmethod
    def sendEmail(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=(data['to_email'],)
          )
        email.send()