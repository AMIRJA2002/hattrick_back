from django.urls import path
from .apis import RegisterApi, RegisterConfirmApi, LoginApi, ConfirmLoginApi

urlpatterns = [
    path('register', RegisterApi.as_view(), name="register"),
    path('register/confirm', RegisterConfirmApi.as_view(), name="confirm"),
    path('login', LoginApi.as_view(), name="login"),
    path('login/confirm', ConfirmLoginApi.as_view(), name="login-confirm"),
    # path('profile/', ProfileApi.as_view(), name="profile"),
]
