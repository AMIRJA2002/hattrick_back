from hattrick.news.serializers import NewMediaSerializer, CategorySerializer
from hattrick.news.models import News, Comment, CommentInteraction
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from hattrick.utils.messages import Message
from rest_framework.views import APIView
import threading

from hattrick.news.selectors import (
    get_news_by_id,
    get_news_by_slug,
    update_comment_by_id,
    delete_comment_by_id,
    get_news_comments_by_id,
    get_comments_reply_by_id,
)
from hattrick.news.services import (
    increase_news_view,
    create_news_interaction,
    create_comment,
    create_comment_interaction,
)

User = get_user_model()


class NewsApi(APIView):
    class NewsOutputSerializer(serializers.ModelSerializer):
        tags = serializers.SerializerMethodField()
        medias = NewMediaSerializer(many=True)
        likes = serializers.CharField()
        category = CategorySerializer()

        class Meta:
            model = News
            fields = ('id', 'slug', 'content', 'summary', 'category', 'tags', 'published_at', 'views', 'is_featured',
                      'is_published', 'medias', 'likes')

        def get_tags(self, obj):
            # Extract only the slugs from the tags and return as a list
            return [tag.slug for tag in obj.tags.all()]

    def get(self, request, id: int = None, slug: str = None):
        news: News = get_news_by_id(id) if id else get_news_by_slug(slug)
        threading.Thread(target=increase_news_view, args=(news,)).start()

        return Response(self.NewsOutputSerializer(instance=news).data, status=status.HTTP_200_OK)


class NewsInteraction(APIView):
    # TODO: we should add unanimous user log for prevent like more than once
    def post(self, request, slug: str):
        create_news_interaction(request.user, slug)
        return Response(Message.news_interaction(), status=status.HTTP_201_CREATED)


class CommentApi(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated()]

    class CommentInputSerializer(serializers.Serializer):
        news = serializers.PrimaryKeyRelatedField(queryset=News.objects.only('id'))
        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.only('id'))
        content = serializers.CharField()
        reply = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.only('id'), required=False)

    class CommentUpdateInputSerializer(serializers.Serializer):
        content = serializers.CharField()

    class CommentOutputSerializer(serializers.ModelSerializer):
        replies_count = serializers.SerializerMethodField()
        likes = serializers.IntegerField()
        dislikes = serializers.IntegerField()

        class Meta:
            model = Comment
            fields = ('user', 'content', 'parent', 'replies_count', 'likes', 'dislikes')

        def get_replies_count(self, obj):
            return obj.get_descendant_count()

    def post(self, request):
        serializer = self.CommentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = create_comment(
            news=serializer.validated_data.get('news'),
            user=serializer.validated_data.get('user'),
            content=serializer.validated_data.get('content'),
            relpy=serializer.validated_data.get('reply'),
        )
        return Response(self.CommentOutputSerializer(instance=comment).data, status=status.HTTP_201_CREATED)

    def get(self, request, id: int):
        comments = get_news_comments_by_id(id=id)
        return Response(self.CommentOutputSerializer(instance=comments, many=True).data, status=status.HTTP_200_OK)

    def patch(self, request, id: int):
        serializer = self.CommentUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = update_comment_by_id(
            id=id,
            user=request.user,
            content=serializer.validated_data.get('content'),
        )
        return Response(self.CommentOutputSerializer(instance=comment).data, status=status.HTTP_200_OK)

    def delete(self, request, id: int):
        threading.Thread(target=delete_comment_by_id, kwargs={'id': id, 'user': request.user}).start()
        return Response(Message.comment_deleted_message(), status=status.HTTP_204_NO_CONTENT)


class CommentReply(APIView):
    class CommentReplyOutputSerialize(serializers.ModelSerializer):
        likes = serializers.IntegerField()
        dislikes = serializers.IntegerField()

        class Meta:
            model = Comment
            fields = ('user', 'content', 'parent', 'likes', 'dislikes')

    def get(self, request, id: int):
        comments = get_comments_reply_by_id(id)
        return Response(self.CommentReplyOutputSerialize(instance=comments, many=True).data, status=status.HTTP_200_OK)


class CommentInteractionApi(APIView):
    permission_classes = (IsAuthenticated,)

    class CommentInteractionSerializer(serializers.ModelSerializer):
        class Meta:
            model = CommentInteraction
            fields = ["comment", "liked", "disliked"]

        def validate(self, data):
            liked = data.get("liked", False)
            disliked = data.get("disliked", False)

            if liked and disliked or not liked and not disliked:
                raise serializers.ValidationError(Message.comment_interaction_both_field_ture_error())

            return data

    def post(self, request):
        serializer = self.CommentInteractionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        like = serializer.validated_data.get('liked')
        dislike = serializer.validated_data.get('disliked')
        comment = serializer.validated_data.get('comment')

        threading.Thread(
            target=create_comment_interaction,
            kwargs={'user': request.user, 'comment': comment, 'like': like, 'dislike': dislike},
            daemon=True,
        ).start()
        return Response(Message.comment_interaction_save())
