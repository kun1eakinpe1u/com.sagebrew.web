import logging

from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api.utils import spawn_task

from .forms import DeleteObjectForm
from .tasks import delete_object_task

logger = logging.getLogger('loggly_logs')


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_object_view(request):
    try:
        delete_object_form = DeleteObjectForm(request.DATA)
        valid_form = delete_object_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form:
        choice_dict = dict(settings.KNOWN_TYPES)
        task_data = {
            "object_type": choice_dict[
                delete_object_form.cleaned_data['object_type']],
            "object_uuid": delete_object_form.cleaned_data['object_uuid'],
            'username': request.user.username,
        }
        spawned = spawn_task(task_func=delete_object_task, task_param=task_data)
        if isinstance(spawned, Exception):
            return Response(status=500)
        return Response(status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)