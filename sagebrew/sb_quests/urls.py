from django.conf.urls import patterns, url

from sb_donations.views import DonationQuestView

from .views import (quest, QuestSettingsView, saga)

urlpatterns = patterns(
    'sb_quests.views',
    # DEPRECATED
    url(r'^/deprecated/(?P<username>[A-Za-z0-9.@_%+-]{2,36})/$', saga,
        name='quest_saga'),

    # Donate
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/'
        r'donate/choose/$', DonationQuestView.as_view(
            template_name='donations/mission.html'),
        name="donation_choose"),

    # Manage
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/banking/$',
        QuestSettingsView.as_view(template_name="manage/quest_banking.html"),
        name="quest_manage_banking"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/billing/$',
        QuestSettingsView.as_view(template_name="manage/quest_billing.html"),
        name="quest_manage_billing"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/add_payment/$',
        QuestSettingsView.as_view(template_name="manage/payment.html"),
        name="quest_add_payment"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/plan/$',
        QuestSettingsView.as_view(template_name="manage/plan.html"),
        name="quest_plan"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/delete/$',
        QuestSettingsView.as_view(template_name="manage/quest_delete.html"),
        name="quest_delete_page"),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/general/$',
        QuestSettingsView.as_view(), name='quest_manage_settings'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/manage/insights/$',
        QuestSettingsView.as_view(template_name="manage/insights.html"),
        name="quest_stats"),

    # View
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/$', quest, name='quest'),


)
