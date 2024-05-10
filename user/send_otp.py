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


def send_email(email, type, amount, account_number, balance):
    if type == 'cr':
        type = "Credited"
    else:
        type = 'Debited'

    account_number= account_number[-4:]

    subject = 'Account Transaction Alert'
    message = f'Your account ending with {account_number} has a {type} of Rs {amount}. Final balance: {balance}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def send_forget_password_mail(email, token):
    subject = 'Your  password rest link'
    message = f'Click the link to register http://127.0.0.1:8000/change_password/{token}/'
    print(message)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True


def regtion_mail(email, data):
    subject = 'Your profile registered'
    message = f'Your profile registration is completed successfully your customer id  {data}'
    print(message)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def regtion_mail_staff(email, data,staff_email,staff_login_register):
    subject = 'Your profile registered'
    message = f'Your staff profile registration is completed successfully.' \
              f' Your staff email {staff_email} staff id is {data}. Click the link to Register Staff Portal {staff_login_register}'
    print(message)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
