from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns(
    'help_center.views',
    url(r'^participate_in_the_conversation/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Participate in the Conversation",
            "description": "Everyone starts out with the privilege of partaking"
                           " in the conversation on Sagebrew.",
            "content_path":
                "%s/static/rendered_docs/"
                "participate_in_the_conversation.html" % (
                    settings.STATIC_URL)
        },
        name="participate_in_the_conversation"),
    url(r'^upvote/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Upvote",
            "description": "Upvoting allows you to showcase your support for "
                           "different pieces of the Conversation!",
            "content_path":
                "%s/static/rendered_docs/10_upvote.html" % (settings.STATIC_URL)
        },
        name="upvote"),
    url(r'^comment/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Comment",
            "description": "Commenting helps to foster communication and allows"
                           " members to provide feedback on other pieces of "
                           "content. This allows for Questions and Solutions to"
                           " constantly evolve and move towards the best "
                           "result.",
            "content_path":
                "%s/static/rendered_docs/20_comment.html" % (settings.STATIC_URL)
        },
        name="comment"),
    url(r'^flagging/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Flag",
            "description": "Flagging empowers the Community to keep the forum "
                           "clean and reduce the noise going into a"
                           " Conversation.",
            "content_path":
                "%s/static/rendered_docs/50_flagging.html" % (settings.STATIC_URL)
        },
        name="flagging"),
    url(r'^downvote/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Downvote",
            "description": "Downvoting in the Public Conversation area allows "
                           "you to privately disclose negative feelings towards"
                           " a given Question, Solution, or Comment.",
            "content_path":
                "%s/static/rendered_docs/100_downvote.html" % (
                    settings.STATIC_URL)
        },
        name="downvote"),
    url(r'^explicit_content/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Explicit Content",
            "description": "Sometimes explicit content can lend itself to "
                           "highlighting the urgency of a Question or "
                           "showcasing the need for a Solution. Abusing this "
                           "privilege can quickly result in your loss of it.",
            "content_path":
                "%s/static/rendered_docs/250_explicit_content.html" % (
                    settings.STATIC_URL)
        },
        name="explicit_content"),
    url(r'^barista/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Barista",
            "description": "Barista is the first rank you can reach! With it "
                           "come some additional privileges.",
            "content_path":
                "%s/static/rendered_docs/1000_barista.html" % (
                    settings.STATIC_URL)
        },
        name="barista"),
    url(r'^tagging/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Tagging",
            "description": "You can now create new Tags that you and other "
                           "members can use to further define "
                           "Conversations.",
            "content_path":
                "%s/static/rendered_docs/1250_tagging.html" % (
                    settings.STATIC_URL)
        },
        name="tagging"),
    url(r'^brewmaster/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Brewmaster",
            "description": "Welcome to the Admin Council, you now how the "
                           "responsibility of a moderator. Thank you for all of"
                           " the amazing contributions you've made and the "
                           "changes you've enabled. We want to empower you to "
                           "do more for the community.",
            "content_path":
                "%s/static/rendered_docs/10000_brewmaster.html" % (
                    settings.STATIC_URL)
        },
        name="brewmaster"),
    url(r'^tribune/$', TemplateView.as_view(
        template_name="help_page.html"),
        kwargs={
            "title": "Tribune",
            "description": "",
            "content_path":
                "%s/static/rendered_docs/12500_tribune.html" % (
                    settings.STATIC_URL)
        },
        name="tribune"),
)