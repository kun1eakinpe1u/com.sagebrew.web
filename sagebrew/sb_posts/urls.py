from django.conf.urls import url
from django.views.generic.base import TemplateView


urlpatterns = [
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/',
        TemplateView.as_view(template_name="single_object.html"),
        name="single_post_page")
]
