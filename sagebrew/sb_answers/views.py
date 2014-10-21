import pytz
import logging
from json import dumps
from datetime import datetime
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)

from .forms import (SaveAnswerForm, EditAnswerForm, VoteAnswerForm,
                    GetAnswerForm)
from .tasks import (save_answer_task, edit_answer_task, vote_answer_task)
from api.utils import spawn_task
from plebs.neo_models import Pleb

logger = logging.getLogger('loggly_logs')

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_answer_view(request):
    '''
    The api endpoint which takes a dictionary to create an answer to a question

    :param request:

                    dict = {'content': '', 'current_pleb': '',
                            'question_uuid': '', 'to_pleb': ''}

    :return:
    '''
    answer_data = request.DATA
    if type(answer_data) != dict:
        return Response({'detail': 'Please provide a valid JSON object'}, status=400)
    #answer_data['content'] = language_filter(answer_data['content'])

    answer_form = SaveAnswerForm(answer_data)
    if answer_form.is_valid():
        spawn_task(task_func=save_answer_task, task_param=answer_form.cleaned_data)
        return Response({'detail': 'successfully posted an answer'}, status=200)
    else:
        return Response({'detail': 'failed to post an answer'}, status=400)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def edit_answer_view(request):
    '''
    The api endpoint which takes a dictionary to edit an answer

    :param request:

                    dict = {'content': '', 'current_pleb': '',
                            'answer_uuid': ''}

    :return:
    '''
    answer_data = request.DATA
    if type(answer_data) != dict:
        return Response({"details": "Please provide a valid JSON object"},
                        status=400)
    answer_data['last_edited_on'] = datetime.now(pytz.utc)
    try:
        answer_data['last_edited_on'] = datetime.now(pytz.utc)
    except TypeError:
        answer_data = answer_data
    answer_form = EditAnswerForm(answer_data)
    if answer_form.is_valid():
        spawn_task(task_func=edit_answer_task,
                   task_param=answer_form.cleaned_data)
        return Response({"detail": "edit question task spawned"},
                        status=200)
    else:
        return Response(answer_form.errors, status=400)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def vote_answer_view(request):
    '''
    The api endpoint which takes a dictionary and allows users to upvote
    or downvote an answer

    :param request:

                    dict = {'current_pleb': '', 'vote_type': '',
                            'answer_uuid': ''}

    :return:
    '''
    try:
        post_data = request.DATA
        if type(post_data) != dict:
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        answer_form = VoteAnswerForm(post_data)
        if answer_form.is_valid():
            spawn_task(task_func=vote_answer_task,
                       task_param=answer_form.cleaned_data)
            return Response({"detail": "Vote Created!"}, status=200)
        else:
            return Response({'detail': answer_form.errors}, status=400)
    except Exception, e:
        logger.exception(dumps({"function": vote_answer_view.__name__,
                                "excpetion": "UnhandledException: "}))
        return Response({"detail": "Vote could not be created!",
                         'exception': e})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def flag_answer_view(request):
    pass