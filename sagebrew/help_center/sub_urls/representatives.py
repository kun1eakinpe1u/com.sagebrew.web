from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^donation_goals/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What are donation goals and how should I set them?",
            "description": "Donation Goals give Representatives and Candidates "
                           "a pragmatic way of interacting with their "
                           "constituents. Gaining donations in turn for "
                           "updates on how the funds are being used.",
            "content_path":
                "%sdonation_goals.html" % (settings.HELP_DOCS_PATH),
            "category": "representatives"
        },
        name="donation_goals"),
    url(r'^funding_not_in_account/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "I've reached my Donation Goal but there are no funds in"
                     " my bank account",
            "description": "Sometimes there are issues with releasing funds."
                           " Have you provided an update for your last Goal?"
                           " There might be issues with your account "
                           "information. Contact us and we'll help figure it "
                           "out.",
            "content_path":
                "%sfunding_not_in_account.html" % (settings.HELP_DOCS_PATH),
            "category": "representatives"
        },
        name="funding_not_in_account"),
    url(r'^how_to_export_contributions/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "I need to file my contributions, how do I retrieve the "
                     "ones I received through Sagebrew?",
            "description": "Short description of how representatives can export"
                           " the information associated with the the "
                           "contributions they've received.",
            "content_path":
                "%show_export_contributions.html" % (settings.HELP_DOCS_PATH),
            "category": "representatives"
        },
        name="how_to_export_contributions"),
    url(r'^how_to_get_on_the_ballot/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I get my name on the ballot?",
            "description": "Brief explanation on how a candidate goes about "
                           "getting their name on the ballot.",
            "content_path":
                "%show_to_get_name_on_ballot.html" % (settings.HELP_DOCS_PATH),
            "category": "representatives"
        },
        name="how_to_get_on_the_ballot"),
    url(r'^name_on_ballot_to_run/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Do I have to have my name on the ballot to run for "
                     "federal office?",
            "description": "Many candidates may wonder if they need to have "
                           "their name on the ballot to run for office. This "
                           "article provides an answer to that question.",
            "content_path":
                "%sname_on_ballot_to_run.html" % (settings.HELP_DOCS_PATH),
            "category": "representatives"
        },
        name="name_on_ballot_to_run"),
    url(r'^need_more_help_public_official/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What if I need more help",
            "description": "Getting more help is just a click away, please"
                           " let us know what you need assistance with!",
            "content_path":
                "%sneed_more_help_repsagetribune.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "representatives"
        },
        name="need_more_help_repsagetribune"),
    url(r'^principal_campaign_committee/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "What is a principal campaign committee?",
            "description": "This is your campaign team.",
            "content_path":
                "%swhat_is_principle_campaign_committee.html" % (
                    settings.HELP_DOCS_PATH),
            "category": "representatives"
        },
        name="principle_campaign_committee"),
    url(r'^suspicious_public_servants/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "How do I report suspicious activity by a Representative?",
            "description": "Sagebrew does its best to make sure all "
                           "candidates and representatives are using the site "
                           "in a legal and positive manner. We welcome the "
                           "assistance of the community.",
            "content_path":
                "%ssuspicious_public_servants.html" % (settings.HELP_DOCS_PATH),
            "category": "representatives"
        },
        name="suspicious_public_servants"),
)