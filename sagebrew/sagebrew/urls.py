from os import environ

from django.conf.urls import include
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView, RedirectView
from django.conf.urls import patterns, url

from sb_registration.views import login_view, logout_view

urlpatterns = patterns(
    '',
    (r'^favicon.ico$', RedirectView.as_view(url="%sfavicon.ico" % (
        settings.STATIC_URL))),
    (r'^$', include('sb_registration.urls')),
    url(r'^login/$', login_view, name="login"),
    url(r'^logout/$', logout_view, name="logout"),
    url(r'^404/$', TemplateView.as_view(template_name="404.html"),
        name="404_Error"),
    (r'^contact_us/$', TemplateView.as_view(template_name="contact_us.html")),
    (r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
    (r'^registration/', include('sb_registration.urls')),
    (r'^comments/', include('sb_comments.urls')),
    (r'^posts/', include('sb_posts.urls')),
    (r'^notifications/', include('sb_notifications.urls')),
    (r'^relationships/', include('sb_relationships.urls')),
    (r'^user/', include('plebs.urls')),
    (r'^questions/', include('sb_questions.urls')),
    (r'^answers/', include('sb_answers.urls')),
    (r'^search/', include('sb_search.urls')),
    (r'^tags/', include('sb_tag.urls')),
    (r'^flag/', include('sb_flags.urls')),
    (r'^vote/', include('sb_votes.urls')),
    (r'^edit/', include('sb_edits.urls')),
    (r'^delete/', include('sb_deletes.urls')),
    (r'^help/', include('help_center.urls')),
)

if settings.DEBUG is True:
    urlpatterns += patterns(
        (r'^admin/', include('admin_honeypot.urls')),
        (r'^secret/', include(admin.site.urls))
    )

if environ.get("CIRCLE_BRANCH", "") == "staging":
    urlpatterns += patterns(
        (r'^admin/', include('admin_honeypot.urls')),
        (r'^secret/', include(admin.site.urls)),
        (r'^robots.txt$', RedirectView.as_view(url="%srobots_staging.txt" % (
            settings.STATIC_URL))),
    )
else:
    urlpatterns += patterns(
        (r'^robots.txt$', RedirectView.as_view(url="%srobots.txt" % (
            settings.STATIC_URL))),
    )