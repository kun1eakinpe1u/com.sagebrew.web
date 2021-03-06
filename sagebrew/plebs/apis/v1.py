from django.conf.urls import patterns, url, include

from rest_framework import routers

from plebs.endpoints import (UserViewSet, ProfileViewSet,
                             SentFriendRequestViewSet, MeViewSet,
                             FriendManager, FriendRequestList,
                             PasswordReset, ResendEmailVerification)
from sb_posts.endpoints import (WallPostsRetrieveUpdateDestroy,
                                WallPostsListCreate)

router = routers.SimpleRouter()
me_router = routers.SimpleRouter()
# We could potentially make these nested but currently separated
# as specific actions may be associated with a profile that will
# also require nesting. We will also have alternative types of users
# that may need additional endpoints
router.register(r'users', UserViewSet, base_name="user")
router.register(r'profiles', ProfileViewSet, base_name="profile")
me_router.register(r'sent_friend_requests', SentFriendRequestViewSet,
                   base_name="sent_friend_request")
router.register(r'me', MeViewSet, base_name="me")

me_router.register(r'friend_requests', FriendRequestList,
                   base_name="friend_request")


urlpatterns = patterns(
    'plebs.endpoints',
    url(r'^me/', include('sb_notifications.apis.relations.v1')),
    url(r'^me/resend_verification/$', ResendEmailVerification.as_view(),
        name='me-resend-verification'),
    url(r'^me/', include(me_router.urls)),
    url(r'^me/friends/(?P<friend_username>[A-Za-z0-9.@_%+-]{2,30})/$',
        FriendManager.as_view(), name="friend-detail"),
    url(r'^reset_password/', PasswordReset.as_view(),
        name='profile-reset-password'),
    url(r'^', include(router.urls)),
    url(r'^profiles/(?P<username>[A-Za-z0-9.@_%+-]{2,30})/wall/$',
        WallPostsListCreate.as_view(), name="profile-wall"),
    url(r'^profiles/(?P<username>[A-Za-z0-9.@_%+-]{2,30})/wall/'
        r'(?P<post_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        WallPostsRetrieveUpdateDestroy.as_view(),
        name="profile-post")
)
