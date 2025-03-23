from hattrick.news.models import News, Interaction, Comment, CommentInteraction
from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model

from django.db import transaction

User = get_user_model()


@transaction.atomic
def increase_news_view(news: News) -> None:
    news.views += 1
    news.save()


def create_news_interaction(user: User, slug: str) -> None:
    news = get_object_or_404(News, slug=slug)
    if not user.is_authenticated:
        Interaction.objects.create(news=news, liked=True)
        return

    interaction, created = Interaction.objects.get_or_create(news=news, user=user)

    if not created:  # If the interaction already exists, toggle the liked status
        interaction.liked = not interaction.liked
        interaction.save()
        return

    interaction.liked = True
    interaction.save()


def create_comment(news: News, user: User, content: str, relpy: int = None) -> Comment:
    comment = Comment(news=news, user=user, content=content)
    if relpy:
        comment.reply = relpy
    comment.save()

    return comment


def create_comment_interaction(user: User, comment: Comment, like: bool, dislike: bool) -> None:
    interaction, created = CommentInteraction.objects.get_or_create(comment=comment, user=user)
    print(40 * 'A')
    print(like)
    if like:
        print(40 * '*')
        interaction.liked = not interaction.liked
        interaction.disliked = False
    elif dislike:
        print(40 * 'B')

        interaction.disliked = not interaction.disliked
        interaction.liked = False

    interaction.save()
    return
