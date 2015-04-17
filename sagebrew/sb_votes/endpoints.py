import pytz
from datetime import datetime

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView)

from sb_base.views import ObjectRetrieveUpdateDestroy
from sb_docstore.utils import add_object_to_table, update_vote, get_vote

from .serializers import VoteSerializer
from .neo_models import Vote


class ObjectVotesRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    # Currently this is not in use as people cannot access votes directly
    # we aren't storing off votes in Neo other than counts on objects
    serializer_class = VoteSerializer
    lookup_field = "object_uuid"
    lookup_url_kwarg = "comment_uuid"

    def get_object(self):
        return Vote.nodes.get(object_uuid=self.kwargs[self.lookup_url_kwarg])


class ObjectVotesListCreate(ListCreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        # Currently we don't do a queryset on votes. Instead we have counts
        # associated with the give objects the votes are on and update those
        # based on the values put into Dynamo
        return []

    def create(self, request, *args, **kwargs):
        now = unicode(datetime.now(pytz.utc))
        vote_data = request.data
        serializer = self.get_serializer(data=vote_data)
        if serializer.is_valid():
            parent_object_uuid = self.kwargs[self.lookup_field]

            status = int(serializer.data['vote_type'])
            vote_data = {
                "parent_object": parent_object_uuid,
                "user": request.user.username,
                "status": status,
                "time": now
            }
            res = get_vote(parent_object_uuid, user=request.user.username)
            if isinstance(res, Exception) is True:
                return Response({"detail": "server error"}, status=500)
            if not res:
                add_res = add_object_to_table('votes', vote_data)
                if isinstance(add_res, Exception) is True:
                    return Response({"detail": "server error"}, status=500)
            else:
                update = update_vote(parent_object_uuid, request.user.username,
                                     status, now)
                if isinstance(update, Exception) is True:
                    return Response({"detail": "server error"}, status=500)

            return Response({"detail": "success"}, status=200)
        else:
            return Response({"detail": "invalid form"}, status=400)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def vote_list(request):
    # TODO instead want to make a list of all the user's existing votes that
    # has a IsSelf permission set. This will enable us to eventually allow users
    # to get to all the items they've voted on and do an analysis of the info
    response = {"status": status.HTTP_501_NOT_IMPLEMENTED,
                "detail": "We do not allow users to query all the votes on"
                          "the site.",
                "developer_message":
                    "Please access votes per user and total counts via their "
                    "corresponding content object."
                }
    return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)