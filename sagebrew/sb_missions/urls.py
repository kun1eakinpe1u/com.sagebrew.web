from django.conf.urls import patterns, url

from sb_donations.views import DonationMissionView
from .views import (public_office_mission, advocate_mission, select_mission,
                    mission, mission_redirect_page, mission_updates,
                    MissionSettingsView, mission_list, mission_edit_updates)


urlpatterns = patterns(
    'sb_missions.views',
    # List
    url(r'^$', mission_list, name='mission_list'),

    # Setup
    url(r'^select/$', select_mission, name="select_mission"),
    url(r'^public_office/$', public_office_mission,
        name="public_office_mission"),
    url(r'^advocate/$', advocate_mission, name="advocate_mission"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/$',
        mission_redirect_page, name="mission_redirect"),

    # Manage
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
        r'manage/updates/$',
        MissionSettingsView.as_view(template_name='manage/updates.html'),
        name="mission_update_settings"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/updates/(?P<edit_id>[A-Za-z0-9.@_%+-]{36})/edit/$',
        mission_edit_updates,
        name="mission_edit_update"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'manage/insights/$',
        MissionSettingsView.as_view(
            template_name='manage/mission_insights.html'),
        name="mission_insights"),

    # Donate
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'donate/amount/$', DonationMissionView.as_view(),
        name="mission_donation_amount"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'donate/name/$',
        DonationMissionView.as_view(template_name='donations/name.html'),
        name="mission_donation_name"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/'
        r'donate/payment/$',
        DonationMissionView.as_view(template_name='donations/payment.html'),
        name="mission_donation_payment"),

    # View
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/updates/$',
        mission_updates, name="mission_updates"),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/(?P<slug>[-\w]+)/$',
        mission, name="mission"),
)
