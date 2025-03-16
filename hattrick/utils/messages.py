class Message:
    @staticmethod
    def phone_register_message():
        return {"msg": "a code has been sent to your phone number"}

    @staticmethod
    def email_register_message():
        return {"msg": "a code has been sent to your email"}

    @staticmethod
    def register_message():
        return {"msg": "a code has been sent to your email or phone number"}

    @staticmethod
    def register_bad_request():
        return {'mgs': 'phone or email is required'}

    @staticmethod
    def register_email_otp_message(otp: int):
        return f'Enter this code {otp} to the site'

    @staticmethod
    def email_exists_message():
        return {'msg': 'a user with this email exists'}

    @staticmethod
    def phone_exists_message():
        return {'msg': 'a user with this phone exists'}

    @staticmethod
    def invalid_otp():
        return {"msg": "Invalid code"}

    @staticmethod
    def user_not_found():
        return {'msg': 'user not found'}