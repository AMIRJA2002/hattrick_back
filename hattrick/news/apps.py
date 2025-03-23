from django.apps import AppConfig

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hattrick.news'

    def ready(self):
        import hattrick.news.signals