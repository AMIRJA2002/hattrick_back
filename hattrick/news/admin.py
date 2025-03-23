from django.contrib import admin
from django.utils.html import format_html
from .models import News, Author, Category, Tag, Media, Interaction, Comment, CommentInteraction, NewsMedia


class MediaInline(admin.TabularInline):
    model = NewsMedia


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "category", "published_at", "is_published", "is_featured", "view_count", 'tags_display')
    list_filter = ("is_published", "is_featured", "category", "tags")
    search_fields = ("title", "content", "summary")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author", "category", "tags")
    date_hierarchy = "published_at"
    actions = ["publish_news", "unpublish_news"]
    inlines = [MediaInline]

    def view_count(self, obj):
        return obj.views

    view_count.short_description = "View Count"

    def publish_news(self, request, queryset):
        queryset.update(is_published=True)

    publish_news.short_description = "Mark selected news as published"

    def unpublish_news(self, request, queryset):
        queryset.update(is_published=False)

    unpublish_news.short_description = "Mark selected news as unpublished"

    def tags_display(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    tags_display.short_description = 'Tags'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "profile_image_preview")
    search_fields = ("user__phone_number", "bio")
    raw_id_fields = ("user",)

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_image.file.url)
        return "No Image"

    profile_image_preview.short_description = "Profile Image"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(NewsMedia)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("news", "file", "media_type", "media_preview")
    list_filter = ("media_type",)

    def media_preview(self, obj):
        if obj.media_type == "image" and obj.file:
            return format_html('<img src="{}" width="100" height="100" />', obj.file.url)
        return "No Preview"

    media_preview.short_description = "Preview"


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("file", "media_type", "media_preview")
    list_filter = ("media_type",)

    def media_preview(self, obj):
        if obj.media_type == "image" and obj.file:
            return format_html('<img src="{}" width="100" height="100" />', obj.file.url)
        return "No Preview"

    media_preview.short_description = "Preview"


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("news", "user", "liked")
    list_filter = ("liked",)
    search_fields = ("news__title", "user__phone_number")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', "news", "user", "content", "parent")
    search_fields = ("news__title", "user__phone_number", "content")


@admin.register(CommentInteraction)
class CommentInteractionAdmin(admin.ModelAdmin):
    list_display = ("comment", "user", "liked", "disliked")
    list_filter = ("liked", "disliked")
    search_fields = ("comment__content", "user__phone_number")
