from django.urls import path, include

urlpatterns = [
    # path('blog/', include(('hattrick.blog.urls', 'blog')))
    path('user/', include(('hattrick.users.urls', 'user')))
]
