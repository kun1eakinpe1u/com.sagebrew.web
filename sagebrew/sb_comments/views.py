import pytz
import logging
from urllib2 import HTTPError
from datetime import datetime
from requests import ConnectionError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from sb_posts.neo_models import SBPost
from api.utils import comment_to_garbage, spawn_task
from .tasks import submit_comment_on_post
from .utils import (get_post_comments)
from .forms import (SaveCommentForm, EditCommentForm, DeleteCommentForm)

logger = logging.getLogger('loggly_logs')


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_comment_view(request):
    '''
    Creates the comment, connects it to whatever parent it was posted on(posts,
    questions, answers)

    Transition from spawning tasks to calling utils to prevent race conditions.

        ex. User creates comment then deletes before the comment creation
        task is
        handled by a worker. This is more likely in a distributed worker queue
        when we have multiple celery workers on multiple servers.

    :param request:
    :return:
    '''
    try:
        comment_info = request.DATA
        if (type(comment_info) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        comment_form = SaveCommentForm(comment_info)
        if comment_form.is_valid():
            spawn_task(task_func=submit_comment_on_post,
                       task_param=comment_form.cleaned_data)
            return Response({"here": "Comment succesfully created"},
                            status=200)
        else:
            return Response({'detail': comment_form.errors}, status=400)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create comment task"},
                        status=408)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_comment(request):  # task
    '''
    Allow plebs to delete their comment

    :param request:
    :return:
    '''
    try:
        comment_info = request.DATA
        if (type(comment_info) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        comment_form = DeleteCommentForm(comment_info)
        if comment_form.is_valid():
            comment_to_garbage(comment_form.cleaned_data['comment_uuid'])
            return Response({"detail": "Comment deleted"}, status=200)
        else:
            return Response({"detail": comment_form.errors}, status=400)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to delete comment"})
        # do stuff with post_info


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_comments(request):
    '''
    Use to return the most recent/top comments, used as a filter
    to show comments on profile page

    :param request:
    :return:
    '''
    my_post = SBPost.nodes.get(sb_id=request.DATA['sb_id'])
    comments = get_post_comments(my_post)
    return Response(comments, status=200)