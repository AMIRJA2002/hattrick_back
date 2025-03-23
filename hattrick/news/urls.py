from django.urls import path
from .apis import NewsApi, NewsInteraction, CommentApi, CommentReply, CommentInteractionApi

app_name = 'news'

urlpatterns = [
    path('comment/', CommentApi.as_view(), name="comment"),
    path('comment/<int:id>/', CommentApi.as_view(), name="news-comments"),
    path('comment/<int:id>/', CommentApi.as_view(), name="update-comment"),
    path('comment/<int:id>/', CommentApi.as_view(), name="delete-comment"),
    path('replies/<int:id>/', CommentReply.as_view(), name="replies"),
    path('comment/interaction/', CommentInteractionApi.as_view(), name="comment-interaction"),
    path('<int:id>/', NewsApi.as_view(), name="news-by-id"),
    path('<slug:slug>/', NewsApi.as_view(), name="news-by-slug"),
    path('like/<slug:slug>/', NewsInteraction.as_view(), name="interaction"),
]
