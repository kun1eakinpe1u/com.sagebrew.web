from django.conf.urls import patterns, url

from .views import edit_object_view, edit_title_view

urlpatterns = patterns('sb_edits.views',
                       url(r'^edit_object_content_api/$', edit_object_view,
                           name='edit_object_content'),
                       url(r'^edit_title_api/$',
                           edit_title_view,
                           name='edit_title'),
)