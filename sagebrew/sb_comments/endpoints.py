from uuid import uuid1
from dateutil import parser

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.reverse import reverse
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView)

from neomodel import db

from api.utils import spawn_task
from sb_base.neo_models import SBContent
from sb_base.views import ObjectRetrieveUpdateDestroy
from plebs.neo_models import Pleb

from .tasks import spawn_comment_notifications
from .neo_models import Comment
from .serializers import CommentSerializer


class ObjectCommentsRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = CommentSerializer
    lookup_field = "object_uuid"
    lookup_url_kwarg = "comment_uuid"

    def get_object(self):
        return Comment.nodes.get(
            object_uuid=self.kwargs[self.lookup_url_kwarg])


class ObjectCommentsListCreate(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        if self.request.user.is_authenticated():
            query = "MATCH (a:SBContent {object_uuid:'%s'})-[:HAS_A]->" \
                    "(b:Comment) WHERE b.to_be_deleted=false" \
                    " RETURN b ORDER BY b.created DESC" % (
                        self.kwargs[self.lookup_field])
            res, _ = db.cypher_query(query)
        else:
            query = "MATCH (a:SBContent {object_uuid:'%s'})-[:HAS_A]->" \
                    "(b:Comment) WHERE a.visibility='public' AND" \
                    " b.to_be_deleted=false" \
                    " RETURN b ORDER BY b.created DESC" % (
                        self.kwargs[self.lookup_field])
            res, _ = db.cypher_query(query)
        return res

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        [row[0].pull() for row in page]
        page = [Comment.inflate(row[0]) for row in page]
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            pleb = Pleb.get(request.user.username)
            parent_object = SBContent.nodes.get(
                object_uuid=self.kwargs[self.lookup_field])
            instance = serializer.save(owner=pleb, parent_object=parent_object)
            serializer_data = serializer.data
            serializer_data['comment_on'] = reverse(
                '%s-detail' % parent_object.get_child_label().lower(),
                kwargs={'object_uuid': parent_object.object_uuid},
                request=request)
            serializer_data['url'] = parent_object.get_url(request=request)
            notification_id = str(uuid1())
            spawn_task(task_func=spawn_comment_notifications, task_param={
                'from_pleb': request.user.username,
                'parent_object_uuid': self.kwargs[self.lookup_field],
                'object_uuid': instance.object_uuid,
                'notification_id': notification_id,
                'comment_on_comment_id': str(uuid1())
            })
            if request.query_params.get('html', 'false').lower() == "true":
                serializer_data['last_edited_on'] = parser.parse(
                    serializer_data['last_edited_on']).replace(microsecond=0)
                serializer_data['created'] = parser.parse(
                    serializer_data['created']).replace(microsecond=0)
                return Response(
                    {
                        "html": [render_to_string(
                            'comment.html',
                            RequestContext(request, serializer_data))],
                        "ids": [serializer_data["object_uuid"]]
                    },
                    status=status.HTTP_200_OK)
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticatedOrReadOnly,))
def comment_renderer(request, object_uuid=None):
    """
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    """
    html_array = []
    id_array = []
    comments = ObjectCommentsListCreate.as_view()(
        request, object_uuid=object_uuid)
    # reasoning behind [::-1] is here
    # http://stackoverflow.com/questions/10201977/how-to-reverse-tuples-in-python?lq=1
    # basically using [::-1] allows us to loop through the list backwards
    # without creating a new variable, also this method works for tuples,
    # lists, dict
    # We need to order the cypher query as DESC and then flip it here to
    # make the ordering of comments work properly after reaching 3 and
    # needing to populate the more comments button.
    for comment in comments.data['results'][::-1]:
        comment['last_edited_on'] = parser.parse(
            comment['last_edited_on']).replace(microsecond=0)
        comment['created'] = parser.parse(
            comment['created']).replace(microsecond=0)
        html_array.append(render_to_string(
            'comment.html', RequestContext(request, comment)))
        id_array.append(comment["object_uuid"])
    comments.data['results'] = {"html": html_array, "ids": id_array}
    return Response(comments.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def comment_list(request):
    response = {"status": status.HTTP_501_NOT_IMPLEMENTED,
                "detail": "We do not allow users to query all the comments on"
                          " the site.",
                "developer_message":
                    "We're working on enabling easier access to comments based"
                    "on user's friends and walls they have access to. "
                    "However this endpoint currently does not return any "
                    "comment data. Please use th other content endpoints to"
                    " reference the comments on them."
                }
    return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)
