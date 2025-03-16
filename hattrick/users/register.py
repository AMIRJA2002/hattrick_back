from hattrick.utils.messages import Message
from django.core.mail import send_mail
from abc import ABC, abstractmethod
from config.env import env
import threading


class Register(ABC):

    @abstractmethod
    def send(self, email, code):
        pass


class EmailRegister(Register):

    def send(self, email, code):
        subject = 'Hattric site otp code'
        message = Message.register_email_otp_message(code)
        from_email = env('GOOGLE_EMAIL_HOST_USER')
        recipient_list = [email]
        fail_silently = False
        threading.Thread(target=send_mail, args=(subject, message, from_email, recipient_list, fail_silently)).start()


class SMSRegister(Register):

    def send(self, phone, code):
        return f"Phone: {phone}"
