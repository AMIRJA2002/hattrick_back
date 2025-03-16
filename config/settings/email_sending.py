from config.env import env, env_to_enum

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = env('GOOGLE_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('GOOGLE_EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False


# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'hamedmirzaei2001official@gmail.com'
# EMAIL_HOST_PASSWORD = 'uguktxanbhlhqjcg'
# EMAIL_PORT = 587
# DEFAULT_FROM_EMAIL = 'foodOnline Marketplace <django.foodonline@gmail.com>'