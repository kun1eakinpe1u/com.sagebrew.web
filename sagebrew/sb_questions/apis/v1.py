from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_questions.endpoints import QuestionViewSet
from sb_comments.endpoints import (ObjectCommentsListCreate,
                                   ObjectCommentsRetrieveUpdateDestroy,
                                   comment_renderer)
from sb_flags.endpoints import (ObjectFlagsListCreate,
                                ObjectFlagsRetrieveUpdateDestroy,
                                flag_renderer)
from sb_solutions.endpoints import (ObjectSolutionsListCreate,
                                    ObjectSolutionsRetrieveUpdateDestroy,
                                    solution_renderer)

router = routers.SimpleRouter()

router.register(r'questions', QuestionViewSet, base_name="question")

urlpatterns = patterns(
    'sb_questions.endpoints',
    url(r'^', include(router.urls)),

    # Comments
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/$',
        ObjectCommentsListCreate.as_view(), name="question-comments"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/'
        r'comments/render/$',
        comment_renderer, name="question-comments-html"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/'
        r'(?P<comment_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(),
        name="question-comment"),

    # Solutions
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/solutions/$',
        ObjectSolutionsListCreate.as_view(), name="question-solutions"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/'
        r'solutions/render/$',
        solution_renderer, name="question-solution-html"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/solutions/'
        r'(?P<solution_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectSolutionsRetrieveUpdateDestroy.as_view(),
        name="question-solution"),

    # Flags
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/flags/$',
        ObjectFlagsListCreate.as_view(), name="question-flags"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/'
        r'flags/render/$',
        flag_renderer, name="question-flag-html"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/flags/'
        r'(?P<flag_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectFlagsRetrieveUpdateDestroy.as_view(),
        name="question-flag"),
)