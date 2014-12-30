from django.conf.urls import url, patterns

from .views import (representative_page, get_experience_form, get_policy_form,
                    get_rep_info)

urlpatterns = patterns(
    'sb_reps.views',
    url(r'^experience/$', get_experience_form, name="experience"),
    url(r'^policy/$', get_policy_form, name="policy"),
    url(r'^get_info/$', get_rep_info, name="rep_info"),
    url(r'^(?P<rep_id>[A-Za-z0-9.@_%+-]{7,60})/$', representative_page,
        name="rep_page")
    )