from django.contrib.auth import get_user_model
from hattrick.common.models import BaseModel
from django.utils import timezone
from django.db import models

User = get_user_model()


class News(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    author = models.ForeignKey("Author", on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField("Tag", blank=True)
    image = models.ForeignKey("Media", on_delete=models.SET_NULL, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
            whenever news is_publish field set true, save published_at field
        """

        if self.is_published is True:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Author(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ForeignKey("Media", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.phone_number


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Media(BaseModel):
    file = models.FileField(upload_to="news_media/")  # محل ذخیره فایل
    media_type = models.CharField(max_length=10, choices=[("image", "Image"), ("video", "Video")])  # نوع رسانه

    def __str__(self):
        return self.file.name


class Interaction(BaseModel):
    news = models.ForeignKey("News", on_delete=models.CASCADE, related_name="interactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("news", "user")

    def __str__(self):
        return f"{self.user} - {self.news.title} - {'Liked' if self.liked else 'Viewed'}"


class Comment(BaseModel):
    news = models.ForeignKey("News", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    reply = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.phone_number} - {self.news.title}"


class CommentInteraction(BaseModel):
    news = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="interactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    liked = models.BooleanField(default=False)
    disliked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("news", "user")

    def __str__(self):
        return f"{self.user} - {'liked' if self.liked else 'disliked'}"
