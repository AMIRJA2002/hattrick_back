from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # path('blog/', include(('hattrick.blog.urls', 'blog')))
    path('user/', include('hattrick.users.urls', 'user')),
    path('news/', include('hattrick.news.urls', 'news')),
]
