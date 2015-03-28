from uuid import uuid1
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import CypherException

from api.utils import execute_cypher_query, spawn_task
from .forms import (SubmitFriendRequestForm, GetFriendRequestForm,
                    RespondFriendRequestForm)
from .neo_models import FriendRequest
from .tasks import create_friend_request_task
from plebs.neo_models import Pleb


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_friend_request(request):
    '''
    calls the task which creates a friend request, it also creates the id
    for the
    request here

    :param request:
    :return:
    '''
    # TODO return uuid of friend request and add to javascript hide button
    # when uuid received
    # if action is True hide friend request button and show a delete friend
    # request button
    friend_request_data = request.DATA
    try:
        request_form = SubmitFriendRequestForm(friend_request_data)
        # TODO Think we're moving this kind of stuff out to the JS system
        # But until then needs to come after the form since it can cause
        # Type errors if someone passes something other than a dict
        object_uuid = str(uuid1())
        valid_form = request_form.is_valid()
    except AttributeError:
        return Response({'detail': 'attribute error'}, status=400)

    if valid_form is True:
        task_data = {
            "from_username": request_form.cleaned_data['from_username'],
            "to_username": request_form.cleaned_data['to_username'],
            "object_uuid": object_uuid
        }
        spawned = spawn_task(task_func=create_friend_request_task,
                             task_param=task_data)
        if isinstance(spawned, Exception) is True:
            return Response({'detail': 'server error'}, status=500)
        return Response({"action": True,
                         "friend_request_id": object_uuid}, status=200)
    else:
        return Response({'detail': 'invalid form'}, status=400)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_friend_requests(request):
    '''
    gets all friend requests attached to the user and returns
    a list of dictionaries of requests

    :param request:
    :return:
    '''
    requests = []
    try:
        form = GetFriendRequestForm(request.DATA)
        valid_form = form.is_valid()
    except AttributeError:
        return Response({'detail': 'attribute error'}, status=400)

    if valid_form is True:
        query = 'match (p:Pleb) where p.email ="%s" ' \
                'with p ' \
                'match (p)-[:RECEIVED_A_REQUEST]-(r:FriendRequest) ' \
                'where r.seen=False ' \
                'return r' % request.DATA['email']
        friend_requests, meta = execute_cypher_query(query)
        friend_requests = [FriendRequest.inflate(row[0])
                           for row in friend_requests]
        for friend_request in friend_requests:
            request_id = friend_request.object_uuid
            request_dict = {
                'from_name': request.user.get_full_name(),
                'from_email': request.user.email,
                'request_id': request_id}
            requests.append(request_dict)
        return Response(requests, status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def respond_friend_request(request):
    '''
    finds the friend request which is attached to both the from and to user
    then, depending on the response type, either attaches the friend
    relationship
    in each pleb and deletes the request, deletes the request, or lets the
    friend
    request exist to stop the user from sending more but does not notify the
    user
    which blocked them that they have a friend request from them.

    :param request:
    :return:
    '''
    try:
        form = RespondFriendRequestForm(request.DATA)
        valid_form = form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form is True:
        try:
            friend_request = FriendRequest.nodes.get(
                object_uuid=form.cleaned_data['request_id'])
            to_pleb = friend_request.request_to.all()[0]
            from_pleb = friend_request.request_from.all()[0]
        except (FriendRequest.DoesNotExist, Pleb.DoesNotExist, IndexError):
            # TODO should we be doing something different for an index error?
            return Response(status=404)
        except CypherException:
            return Response(status=500)

        if form.cleaned_data['response'] == 'accept':
            rel1 = to_pleb.friends.connect(from_pleb)
            rel2 = from_pleb.friends.connect(to_pleb)
            rel1.save()
            rel2.save()
            friend_request.delete()
            to_pleb.save()
            from_pleb.save()
            return Response(status=200)
        elif form.cleaned_data['response'] == 'deny':
            friend_request.delete()
            return Response(status=200)
        elif form.cleaned_data['response'] == 'block':
            friend_request.seen = True
            friend_request.response = 'block'
            friend_request.save()
            return Response(status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)