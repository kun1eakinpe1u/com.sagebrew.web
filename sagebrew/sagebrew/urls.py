from os import environ

from django.conf.urls import include
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView, RedirectView
from django.conf.urls import patterns, url
from django.contrib.sitemaps.views import sitemap

from sb_registration.views import (login_view, logout_view, signup_view,
                                   quest_signup, advocacy, political_campaign)
from plebs.sitemap import ProfileSitemap
from sb_questions.sitemap import QuestionSitemap
from sagebrew.sitemap import (StaticViewSitemap, SignupSitemap)
from sb_quests.sitemap import QuestSitemap
from sb_missions.sitemap import (MissionSitemap,
                                 MissionUpdateSitemap, MissionListSitemap)
from help_center.sitemap import (AccountHelpSitemap, ConversationHelpSitemap,
                                 DonationsHelpSitemap, PoliciesHelpSitemap,
                                 PrivilegeHelpSitemap, QuestHelpSitemap,
                                 QuestionHelpSitemap,
                                 ReputationModerationHelpSitemap,
                                 SecurityHelpSitemap, SolutionsHelpSitemap,
                                 TermsHelpSitemap)


urlpatterns = patterns(
    '',
    (r'^favicon\.ico$', RedirectView.as_view(url="%s/images/favicon.ico" % (
        settings.STATIC_URL), permanent=True)),
    url(r'^login/$', login_view, name="login"),
    url(r'^logout/$', logout_view, name="logout"),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset',
        {"template_name": "password_reset/password_reset.html"},
        name="reset_password_page"),
    url(r'^password_reset/done/$',
        'django.contrib.auth.views.password_reset_done', {
            "template_name": "password_reset/password_reset_sent.html"},
        name="password_reset_done"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {"template_name": "password_reset/password_change_form.html"},
        name="password_reset_confirm"),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',
        {"template_name": "password_reset/password_reset_done.html"},
        name="password_reset_complete"),
    url(r'^terms/$', RedirectView.as_view(
        url='/help/terms/', permanent=False), name='terms_redirect'),
    url(r'^400/$', TemplateView.as_view(template_name="400.html"),
        name="400_Error"),
    url(r'^401/$', TemplateView.as_view(template_name="401.html"),
        name="401_Error"),
    url(r'^404/$', TemplateView.as_view(template_name="404.html"),
        name="404_Error"),
    url(r'^500/$', TemplateView.as_view(template_name="500.html"),
        name="500_Error"),
    url(r'^contact-us/$', RedirectView.as_view(
        url='/help/policies/support/', permanent=False),
        name='contact_us'),
    url(r'^contact_us/$', RedirectView.as_view(
        url='/contact-us/', permanent=True),
        name='contact_us_redirect'),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    (r'^registration/', include('sb_registration.urls')),
    (r'^help/', include('help_center.urls')),
    (r'^user/', include('plebs.urls')),
    (r'^conversations/', include('sb_questions.urls')),
    (r'^search/', include('sb_search.urls')),
    (r'^quests/', include('sb_public_official.urls')),
    (r'^quests/', include('sb_quests.urls')),
    (r'^missions/', include('sb_missions.urls')),
    (r'^council/', include('sb_council.urls')),
    (r'^posts/', include('sb_posts.urls')),
    (r'^solutions/', include('sb_solutions.urls')),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/',
        TemplateView.as_view(template_name="single_object.html"),
        name="single_question_page"),
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {
            'questions': QuestionSitemap,
            'profiles': ProfileSitemap,
            'quests': QuestSitemap,
            'missions': MissionSitemap,
            'mission_list': MissionListSitemap,
            'updates': MissionUpdateSitemap,
            'static_pages': StaticViewSitemap,
            'sign_up': SignupSitemap,
            'account_help': AccountHelpSitemap,
            'conversation_help': ConversationHelpSitemap,
            'donation_help': DonationsHelpSitemap,
            'policy_help': PoliciesHelpSitemap,
            'privilege_help': PrivilegeHelpSitemap,
            'quest_help': QuestHelpSitemap,
            'question_help': QuestionHelpSitemap,
            'reputation_moderation_help': ReputationModerationHelpSitemap,
            'security_help': SecurityHelpSitemap,
            'solutions_help': SolutionsHelpSitemap,
            'terms_help': TermsHelpSitemap
        }},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^quest/$', quest_signup, name='quest_info'),
    (r'^v1/', include('sb_questions.apis.v1')),
    (r'^v1/', include('sb_solutions.apis.v1')),
    (r'^v1/', include('sb_oauth.apis.v1')),
    (r'^v1/', include('plebs.apis.v1')),
    (r'^v1/', include('sb_address.apis.v1')),
    (r'^v1/', include('sb_posts.apis.v1')),
    (r'^v1/', include('sb_comments.apis.v1')),
    (r'^v1/', include('sb_news.apis.v1')),
    (r'^v1/', include('sb_missions.apis.v1')),
    (r'^v1/', include('sb_privileges.apis.v1')),
    (r'^v1/', include('sb_tags.apis.v1')),
    (r'^v1/', include('sb_updates.apis.v1')),
    (r'^v1/', include('sb_uploads.apis.v1')),
    (r'^v1/', include('sb_quests.apis.v1')),
    (r'^v1/', include('sb_donations.apis.v1')),
    (r'^v1/', include('sb_locations.apis.v1')),
    (r'^v1/', include('sb_council.apis.v1')),
    (r'^v1/', include('sb_search.apis.v1')),
    (r'^v1/', include('sb_accounting.apis.v1')),
    (r'^v1/', include('sb_orders.apis.v1')),
    url(r'^advocacy/$', advocacy, name="advocacy"),
    url(r'^political/$', political_campaign, name="political"),
    url(r'^$', signup_view, name="signup"),
)

if settings.DEBUG is True:
    urlpatterns += patterns(
        '',
        (r'^robots\.txt$', TemplateView.as_view(
            template_name='robots_staging.txt', content_type='text/plain')),
        (r'^loaderio-98182a198e035e1a9649f683fb42d23e/$', TemplateView.as_view(
            template_name='external_tests/loaderio.txt',
            content_type='text/plain')),
        (r'^14c08cb7770b778cba5856e49dbf24d3d8a2048e.html$',
         TemplateView.as_view(
             template_name='external_tests/'
                           '14c08cb7770b778cba5856e49dbf24d3d8a2048e.html',
             content_type='text/plain')),
        (r'^secret/', include(admin.site.urls)),
    )
elif environ.get("CIRCLE_BRANCH", "") == "staging" and settings.DEBUG is False:
    urlpatterns += patterns(
        '',
        (r'^robots\.txt$', TemplateView.as_view(
            template_name='robots_staging.txt', content_type='text/plain')),
        (r'^loaderio-98182a198e035e1a9649f683fb42d23e/$', TemplateView.as_view(
            template_name='external_tests/loaderio.txt',
            content_type='text/plain')),
        (r'^14c08cb7770b778cba5856e49dbf24d3d8a2048e.html$',
         TemplateView.as_view(
             template_name='external_tests/'
                           '14c08cb7770b778cba5856e49dbf24d3d8a2048e.html',
             content_type='text/plain')),
        (r'^secret/', include(admin.site.urls)),
    )
else:
    urlpatterns += patterns(
        '',
        (r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
                                                content_type='text/plain')),
        (r'^d667e6bf-d0fe-4aef-8efe-1e50c18b2aec/', include(admin.site.urls)),
    )
