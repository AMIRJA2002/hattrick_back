from rest_framework.generics import get_object_or_404
from django.db.models import Count, Q, QuerySet
from django.contrib.auth import get_user_model

from .models import News, Comment

User = get_user_model()


def get_news_by_id(id: int) -> News:
    return get_object_or_404(
        News.objects.select_related('category').prefetch_related('medias').annotate(
            likes=Count('interactions', filter=Q(interactions__liked=True))
        ), id=id
    )


def get_news_by_slug(slug: str) -> News:
    return get_object_or_404(
        News.objects.select_related('category').prefetch_related('medias').annotate(
            likes=Count('interactions', filter=Q(interactions__liked=True))
        ), slug=slug
    )


def get_news_comments_by_id(id: int) -> QuerySet[Comment]:
    return Comment.objects.filter(
        news__id=id, parent__isnull=True
    ).annotate(
        likes=Count('interactions', filter=Q(interactions__liked=True)),
        dislikes=Count('interactions', filter=Q(interactions__disliked=True))
    )


def update_comment_by_id(id: int, content: str, user: User) -> Comment:
    comment = get_object_or_404(Comment, user=user, id=id)
    comment.content = content
    comment.save()
    return comment


def delete_comment_by_id(id: int, user: User) -> None:
    get_object_or_404(Comment, id=id, user=user).delete()


def get_comments_reply_by_id(id: int) -> QuerySet[Comment]:
    comment = get_object_or_404(Comment.objects.only('id', 'content'), id=id)
    return comment.get_descendants().annotate(
        likes=Count('interactions', filter=Q(interactions__liked=True)),
        dislikes=Count('interactions', filter=Q(interactions__disliked=True)),
    )
