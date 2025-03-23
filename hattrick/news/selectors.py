from typing import Set, Dict

from rest_framework.generics import get_object_or_404
from django.db.models import Count, Q, QuerySet, Subquery, OuterRef, Prefetch
from django.contrib.auth import get_user_model
from .models import News, Comment, NewsMedia
from hattrick.utils.redis_conn import redis_conn

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


def featured_news_list(key: str) -> list[Dict[str, any]]:
    return redis_conn.get_set_by_key(key)


def get_news_list() -> QuerySet[News]:
    return (News.objects.defer('created_at', 'updated_at', 'slug', 'summary', 'category_id', 'views', 'is_featured', 'is_published').prefetch_related(
        'medias'
    ).annotate(
        image_url=Subquery(NewsMedia.objects.filter(news=OuterRef('pk'), is_head_page=True).values('file')),
        user_data=Subquery(User.objects.filter(id=OuterRef('author__pk')).values('phone_number')),
    ).filter(is_published=True, is_featured=True))
