import threading

from .register import EmailRegister, SMSRegister
from hattrick.utils.redis_conn import redis_conn
from .models import BaseUser, Profile

from django.db import transaction


class RegisterFactoryService:

    @staticmethod
    def send_code(data, code):
        response = {
            'email': EmailRegister,
            'phone': SMSRegister,
        }

        for key, value in data.items():
            if value is not None:
                response[key]().send(value, code)
                return key

        return None


def cache_user_email_and_otp(email, otp, ttl=None):
    threading.Thread(target=redis_conn.set, args=(email, otp, ttl)).start()


def create_profile(*, user: BaseUser) -> Profile:
    return Profile.objects.create(user=user)


def register_confirm(code, email_or_phone):
    if redis_conn.get(email_or_phone) == code:
        return True
    return False


def create_user(*, email: str, phone_number: str) -> BaseUser:
    return BaseUser.objects.create_user(email=email, phone_number=phone_number)


@transaction.atomic
def register(*, email: str, phone_number: str) -> BaseUser:
    user = create_user(email=email, phone_number=phone_number)
    create_profile(user=user)

    return user
