from django.conf.urls import patterns, url

from .views import (save_question_view,
                    close_question_view,
                    get_question_view, submit_question_view_page, question_page,
                    question_detail_page,  get_question_search_view,
                    edit_question_view)

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^$', question_page, name='question_page'),
    url(r'^submit_question/$', submit_question_view_page, name='save_question_page'),
    url(r'^submit_question_api/$', save_question_view, name='save_question'),
    url(r'^query_questions_api/$', get_question_view, name='get_questions'),
    url(r'^close_question_api/$', close_question_view, name='close_question'),
    url(r'^(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/edit/$', edit_question_view,
        name='edit_question_page'),
    url(r'^(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/$', question_detail_page,
        name='question_detail_page'),
    url(r'^search/(?P<question_uuid>[A-Za-z0-9.@_%+-]{36})/$',
        get_question_search_view, name='question_search_page'),
)