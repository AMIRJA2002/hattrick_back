from django.urls import path
from .apis import RegisterApi, RegisterConfirmApi, LoginApi, ConfirmLoginApi, EasyJwt

app_name = 'users'

urlpatterns = [
    path('register/', RegisterApi.as_view(), name="register"),
    path('register/confirm/', RegisterConfirmApi.as_view(), name="confirm"),
    path('login/', LoginApi.as_view(), name="login"),
    path('login/confirm/', ConfirmLoginApi.as_view(), name="login-confirm"),
    path('jwt/', EasyJwt.as_view(), name="easy"),
    # path('profile/', ProfileApi.as_view(), name="profile"),
]
