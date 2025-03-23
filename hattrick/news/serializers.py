from rest_framework import serializers

from hattrick.news.models import Tag, NewsMedia, Interaction, Category


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('slug',)


class NewMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsMedia
        fields = ('file', 'media_type')


class InterActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ('liked',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)