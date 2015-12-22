from django.conf.urls import patterns, url

from .views import (public_office_mission, advocate_mission, select_mission,
                    mission, mission_redirect_page, mission_updates,
                    MissionSettingsView, mission_list)


urlpatterns = patterns(
    'sb_missions.views',
    url(r'^$', mission_list, name='mission_list'),
    url(r'^select/$', select_mission, name="select_mission"),
    url(r'^public_office/$', public_office_mission,
        name="public_office_mission"),
    url(r'^advocate/$', advocate_mission, name="advocate_mission"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/$',
        mission_redirect_page, name="mission_redirect"),
    url(r'^settings/$', MissionSettingsView.as_view(),
        name="mission_settings_redirect"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/general/$',
        MissionSettingsView.as_view(), name="mission_settings"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/epic/$',
        MissionSettingsView.as_view(template_name='manage/epic.html'),
        name="mission_edit_epic"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/goals/$',
        MissionSettingsView.as_view(template_name='manage/goals.html'),
        name="mission_goals_settings"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/updates/$',
        MissionSettingsView.as_view(template_name='manage/updates.html'),
        name="mission_update_settings"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/updates/$',
        mission_updates, name="mission_updates"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/$',
        mission, name="mission"),
)
