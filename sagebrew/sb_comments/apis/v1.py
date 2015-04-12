from django.conf.urls import patterns, url

from rest_framework import routers


from sb_posts.endpoints import (PostsViewSet)

from sb_comments.endpoints import (ObjectCommentsRetrieveUpdateDestroy)

from sb_flags.endpoints import (ObjectFlagsListCreate,
                                ObjectFlagsRetrieveUpdateDestroy,
                                flag_renderer)

router = routers.SimpleRouter()

router.register(r'posts', PostsViewSet, base_name="post")

"""
See sb_questions/apis/v1.py for reasoning on excluding
ObjectCommentsRetrieveUpdateDestroy
"""

urlpatterns = patterns(
    'sb_comments.endpoints',
    url(r'^comments/(?P<comment_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(), name="comment-detail"),
    # Adding in for flags/votes/etc but must be a cleaner process
    url(r'^comments/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(), name="comment-detail"),

    # Flags
    url(r'^comments/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/flags/$',
        ObjectFlagsListCreate.as_view(), name="comment-flags"),
    url(r'^comments/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/'
        r'flags/render/$',
        flag_renderer, name="comment-flag-html"),
    url(r'^comments/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/flags/'
        r'(?P<flag_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectFlagsRetrieveUpdateDestroy.as_view(),
        name="comment-flag"),
)