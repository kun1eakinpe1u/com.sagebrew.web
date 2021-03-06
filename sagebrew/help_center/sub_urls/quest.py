from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView, RedirectView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^funding-not-in-account/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "I've received a Donation but there are no "
                     "funds in my bank account",
            "description": "Funds will usually take up to two full business "
                           "days to transfer into your account. If you're "
                           "having issues though we're happy to help!",
            "content_path":
                "%sfunding_not_in_account.html" % settings.HELP_DOCS_PATH,
            "category": "Quest and Missions"
    },
        name="funding_not_in_account"),
    url(r'^how-to-export-contributions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "I need to file the contributions to my campaign",
            "description": "Short description of how representatives can export"
                           " the information associated with the the "
                           "contributions they've received.",
            "content_path":
                "%show_export_contributions.html" % settings.HELP_DOCS_PATH,
            "category": "Quest and Missions"
    },
        name="how_to_export_contributions"),
    url(r'^how-to-get-on-the-ballot/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I get my name on the ballot?",
            "description": "Brief explanation on how a candidate goes about "
                           "getting their name on the ballot.",
            "content_path":
                "%show_to_get_name_on_ballot.html" % settings.HELP_DOCS_PATH,
            "category": "Quest and Missions"
    },
        name="how_to_get_on_the_ballot"),
    url(r'^how-to-run/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How to run for office",
            "description": "Information on what you need to know if you "
                           "want to run for public office.",
            "content_path":
                "%show_to_run_for_office.html" % settings.HELP_DOCS_PATH,
            "category": "Quest and Missions"
    },
        name="how_to_run"),
    url(r'^name-on-ballot-to-run/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Do I have to have my name on the ballot to run for "
                     "federal office?",
            "description": "Many candidates may wonder if they need to have "
                           "their name on the ballot to run for office. This "
                           "article provides an solution to that question.",
            "content_path":
                "%sname_on_ballot_to_run.html" % settings.HELP_DOCS_PATH,
            "category": "Quest and Missions"
    },
        name="name_on_ballot_to_run"),
    url(r'^need-more-help-public-official/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What if I need more help",
            "description": "Getting more help is just a click away, please"
                           " let us know what you need assistance with!",
            "content_path":
                "%sneed_more_help_repsagetribune.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "Quest and Missions"
    },
        name="need_more_help_repsagetribune"),
    url(r'^update-management/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Managing Updates",
            "description": "This article discusses Mission Updates and "
                           "what they they're designed for.",
            "content_path":
                "%supdate_management.html" % settings.HELP_DOCS_PATH,
            "category": "Quest and Missions"
    },
        name="update_management"),
    url(r'^principal-campaign-committee/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is a principal campaign committee?",
            "description": "This is your campaign team.",
            "content_path":
                "%swhat_is_principle_campaign_committee.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "Quest and Missions"
    },
        name="principle_campaign_committee"),
    url(r'^funding_not_in_account/$', RedirectView.as_view(
        url='/help/quest/funding-not-in-account/', permanent=True),
        name='funding_not_in_account_redirect'),
    url(r'^how_to_export_contributions/$', RedirectView.as_view(
        url='/help/quest/how-to-export-contributions/', permanent=True),
        name='how_to_export_contributions_redirect'),
    url(r'^how_to_get_on_the_ballot/$', RedirectView.as_view(
        url='/help/quest/how-to-get-on-the-ballot/', permanent=True),
        name='how_to_get_on_the_ballot_redirect'),
    url(r'^how_to_run/$', RedirectView.as_view(
        url='/help/quest/how-to-run/', permanent=True),
        name='how_to_run_redirect'),
    url(r'^name_on_ballot_to_run/$', RedirectView.as_view(
        url='/help/quest/name-on-ballot-to-run/', permanent=True),
        name='name_on_ballot_to_run_redirect'),
    url(r'^need_more_help_public_official/$', RedirectView.as_view(
        url='/help/quest/need-more-help-public-official/', permanent=True),
        name='need_more_help_public_official_redirect'),
    url(r'^principal_campaign_committee/$', RedirectView.as_view(
        url='/help/quest/principal-campaign-committee/', permanent=True),
        name='principal_campaign_committee_redirect'),
)
