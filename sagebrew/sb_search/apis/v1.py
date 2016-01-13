from django.conf.urls import patterns, url

from sb_search.endpoints import SearchViewSet

urlpatterns = patterns(
    'sb_search.endpoints',
    url(r'^search/', SearchViewSet.as_view(), name="search-list"),
)