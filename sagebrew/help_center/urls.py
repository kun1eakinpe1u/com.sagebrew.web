from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from sagebrew.help_center.views import related_articles, help_area
'''
content_path is used in sync with the ssi tag in help_page.html to include
the rendered html files from S3. Using python's
http://pythonhosted.org//Markdown/cli.html we can convert the md files into
html in the static folder and then run these right out of the template. This
allows for us to still have a side bar, nav bar, and footer with user centric
material displayed while manging our docs in a markdown format making it easy
for our content creators to manage the information.

'''
urlpatterns = [
    url(r'^questions/', include('sagebrew.help_center.sub_urls.questions')),
    url(r'^solutions/', include('sagebrew.help_center.sub_urls.solutions')),
    url(r'^reputation_and_moderation/', include(
        'sagebrew.help_center.sub_urls.reputation_and_moderation')),
    url(r'^conversation/',
        include('sagebrew.help_center.sub_urls.conversation')),
    url(r'^privileges/', include('sagebrew.help_center.sub_urls.privileges')),
    url(r'^donating/', include('sagebrew.help_center.sub_urls.donations')),
    url(r'^quests/how_to_run/$', RedirectView.as_view(
        url='/help/quest/how-to-run/', permanent=True),
        name='s-how-to-run-redirect'),
    url(r'^quests/how_to_export_contributions/$', RedirectView.as_view(
        url='/help/quest/how-to-export-contributions/', permanent=True),
        name='s-how-to-export-contributions'),
    url(r'^quests/principal_campaign_committee/$', RedirectView.as_view(
        url='/help/quest/principal-campaign-committee/', permanent=True),
        name='s-principal-campaign-committee'),
    url(r'^quests/how_to_get_on_the_ballot/$', RedirectView.as_view(
        url='/help/quest/how-to-get-on-the-ballot/', permanent=True),
        name='s-how-to-get-on-the-ballot'),
    url(r'^quests/name_on_ballot_to_run/$', RedirectView.as_view(
        url='/help/quest/name-on-ballot-to-run/', permanent=True),
        name='name_on_ballot_to_run_redirect'),
    url(r'^quests/need_more_help_public_official/$', RedirectView.as_view(
        url='/help/quest/need-more-help-public-official/', permanent=True),
        name='s-need-more-help-public-official'),
    url(r'^quests/funding_not_in_account/$', RedirectView.as_view(
        url='/help/quest/funding-not-in-account/', permanent=True),
        name='funding_not_in_account_direct_redirect'),
    url(r'^quest/', include('sagebrew.help_center.sub_urls.quest')),
    url(r'^reputation/', include(
        'sagebrew.help_center.sub_urls.reputation_and_moderation')),
    url(r'^accounts/', include('sagebrew.help_center.sub_urls.account')),
    url(r'^security/', include('sagebrew.help_center.sub_urls.security')),
    url(r'^terms/', include('sagebrew.help_center.sub_urls.terms')),
    url(r'^policies/', include('sagebrew.help_center.sub_urls.policies')),
    url(r'^related_articles/$', related_articles, name="related_articles"),
    url(r'^$', help_area, name="help_center")
]

"""
TODO: We need to ensure we do the following to allow indexing and easier search
Title: My super title
Date: 2010-12-03 10:20
Modified: 2010-12-05 19:30
Category: Python
Tags: pelican, publishing
Slug: my-super-post
Authors: Alexis Metaireau, Conan Doyle
Summary: Short version for index and feeds

See http://docs.getpelican.com/en/3.5.0/content.html#file-metadata for html
metadata result
"""
