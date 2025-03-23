from django.db.models import Q

from hattrick.users.services import register, RegisterFactoryService, cache_user_email_and_otp, register_confirm
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from ..utils.messages import Message
from rest_framework import status
from django.contrib.auth import get_user_model
import random

from ..utils.redis_conn import redis_conn

User = get_user_model()


class RegisterApi(APIView):
    class RegisterInputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)
        phone = serializers.CharField(max_length=11, required=False)

    @extend_schema(
        request=RegisterInputSerializer,
        responses={201: Message.email_register_message(), 400: Message.register_bad_request()},
        description="ارسال کد تأیید برای ثبت‌نام با ایمیل یا شماره تلفن"
    )
    def post(self, request):
        serializer = self.RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = random.randint(100000, 999999)

        email = serializer.validated_data.get('email')
        phone = serializer.validated_data.get('phone')

        if email and User.objects.filter(email=email).exists():
            return Response(Message.email_exists_message(), status=status.HTTP_400_BAD_REQUEST)

        if phone and User.objects.filter(phone=phone).exists():
            return Response(Message.phone_exists_message(), status=status.HTTP_400_BAD_REQUEST)

        response = RegisterFactoryService.send_code(data=serializer.validated_data, code=code)

        if response == 'email':
            cache_user_email_and_otp(serializer.validated_data['email'], code, 60 * 2)
            return Response(Message.email_register_message(), status=status.HTTP_201_CREATED)

        if response == 'phone':
            cache_user_email_and_otp(serializer.validated_data['phone'], code)
            return Response(Message.phone_register_message(), status=status.HTTP_201_CREATED)

        return Response(Message.register_bad_request(), status=status.HTTP_400_BAD_REQUEST)


class RegisterConfirmApi(APIView):
    class RegisterConfirmInputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)
        phone = serializers.CharField(max_length=11, required=False)
        code = serializers.CharField(required=True)

    class RegisterConfirmOutputSerializer(serializers.ModelSerializer):
        token = serializers.SerializerMethodField()

        class Meta:
            model = User
            fields = ['id', 'email', 'phone_number', 'created_at', 'token']

        def get_token(self, user):
            data = dict()
            token_class = RefreshToken

            refresh = token_class.for_user(user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data

    @extend_schema(
        request=RegisterConfirmInputSerializer,
        responses={201: RegisterConfirmOutputSerializer, 400: Message.invalid_otp()},
        description="کاربر کد تایید دریافت شده را وارد می‌کند و در صورت صحت، حساب کاربری ایجاد می‌شود.",
    )
    def post(self, request):
        serializer = self.RegisterConfirmInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        contact_field = "email" if validated_data.get("email") else "phone"

        if not validated_data.get(contact_field):
            return Response(Message.register_bad_request(), status=status.HTTP_400_BAD_REQUEST)

        response = register_confirm(code=validated_data['code'], email_or_phone=validated_data[contact_field])

        if not response:
            return Response(Message.invalid_otp(), status=status.HTTP_400_BAD_REQUEST)

        user = register(email=serializer.validated_data['email'], phone_number=serializer.validated_data['phone'])
        redis_conn.delete(serializer.validated_data['email'])
        return Response(self.RegisterConfirmOutputSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginApi(APIView):
    class LoginInputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)
        phone = serializers.CharField(max_length=11, required=False)

    @extend_schema(
        request=LoginInputSerializer,
        responses={201: Message.email_register_message(), 400: Message.register_bad_request()},
        description="کاربر با ایمیل یا شماره تلفن خود درخواست ورود می‌دهد و یک کد تایید دریافت می‌کند.",
    )
    def post(self, request):
        serializer = self.LoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = random.randint(100000, 999999)

        response = RegisterFactoryService.send_code(data=serializer.validated_data, code=code)

        if response == 'email':
            cache_user_email_and_otp(serializer.validated_data['email'], code, 60 * 2)
            return Response(Message.email_register_message(), status=status.HTTP_201_CREATED)

        if response == 'phone':
            cache_user_email_and_otp(serializer.validated_data['phone'], code)
            return Response(Message.phone_register_message(), status=status.HTTP_201_CREATED)

        return Response(Message.register_bad_request(), status=status.HTTP_400_BAD_REQUEST)


class ConfirmLoginApi(APIView):
    class LoginConfirmInputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)
        phone = serializers.CharField(max_length=11, required=False)
        code = serializers.CharField(required=True)

    class LoginConfirmOutputSerializer(serializers.ModelSerializer):
        token = serializers.SerializerMethodField()

        class Meta:
            model = User
            fields = ['id', 'email', 'phone_number', 'created_at', 'token']

        def get_token(self, user):
            data = dict()
            token_class = RefreshToken

            refresh = token_class.for_user(user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data

    @extend_schema(
        request=LoginConfirmInputSerializer,
        responses={201: LoginConfirmOutputSerializer, 400: Message.invalid_otp()},
        description="کاربر کد دریافت شده را وارد می‌کند و در صورت صحت، به سیستم وارد می‌شود.",
    )
    def post(self, request):
        serializer = self.LoginConfirmInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        contact_field = "email" if validated_data.get("email") else "phone"

        if not validated_data.get(contact_field):
            return Response(Message.register_bad_request(), status=status.HTTP_400_BAD_REQUEST)

        response = register_confirm(code=validated_data['code'], email_or_phone=validated_data[contact_field])

        if not response:
            return Response(Message.invalid_otp(), status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(
            Q(email=serializer.validated_data['email']) | Q(phone_number=serializer.validated_data['phone'])
        ).first()

        if not user:
            return Response(Message.user_not_found(), status=status.HTTP_404_NOT_FOUND)

        redis_conn.delete(serializer.validated_data[contact_field])
        return Response(self.LoginConfirmOutputSerializer(user).data, status=status.HTTP_201_CREATED)


class EasyJwt(APIView):
    # @extend_schema(
    #     responses={200: dict(refresh=str, access=str)},
    #     summary="دریافت توکن JWT برای تست",
    #     description="یک کاربر مشخص را پیدا کرده و توکن‌های احراز هویت JWT را برای او برمی‌گرداند.",
    # )
    def get(self, request):
        user = User.objects.get(phone_number='09190257536')
        data = dict()
        token_class = RefreshToken

        refresh = token_class.for_user(user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return Response(data)
