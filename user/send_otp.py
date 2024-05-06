import random
from django.core.mail import send_mail
from django.conf import settings


def send_otp_email(email):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    subject = 'Your OTP for verification'
    message = f'Your OTP is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return otp



# def send_forget_password_mail(email, token):
#     subject = 'Your forget password link'
#     message = f'Click the link to register http://127.0.0.1:8000/account/change_password/{token}/'
#     email_from = settings.EMAIL_HOST_USER
#     recipient_list = [email]
#     send_mail(subject, message, email_from, recipient_list)
#     return True
