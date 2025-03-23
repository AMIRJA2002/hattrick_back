from hattrick.news.services import update_featured_news_cache
from django.db.models.signals import post_save
from hattrick.news.models import News
from django.dispatch import receiver


@receiver(post_save, sender=News)
def update_featured_news_cache_signal(sender, instance, created, **kwargs):
    # threading.Thread(target=update_featured_news_cache)
    update_featured_news_cache()
