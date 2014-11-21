from celery import shared_task

from neomodel.exception import CypherException

from sb_notifications.tasks import spawn_notifications
from api.utils import spawn_task, get_object

from .utils import save_comment, comment_relations


@shared_task()
def save_comment_on_object(content, current_pleb, object_uuid, object_type,
                           comment_uuid):
    '''
    The task which creates a comment and attaches it to an object.

    The objects can be: SBPost, SBAnswer, SBQuestion.

    :param content:
    :param current_pleb:
    :param object_uuid:
    :param object_type:
    :return:
            Will return True if the comment was made and the task to spawn a
            notification was created

            Will return false if the comment was not created
    '''
    sb_object = get_object(object_type, object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise save_comment_on_object.retry(exc=sb_object, countdown=5,
                                           max_retries=None)
    elif sb_object is False:
        return sb_object

    my_comment = save_comment(content, comment_uuid)

    if isinstance(my_comment, Exception) is True:
        raise save_comment_on_object.retry(exc=my_comment, countdown=5,
                                           max_retries=None)
    task_data = {"current_pleb": current_pleb, "comment": my_comment,
                 "sb_object": sb_object}
    spawned = spawn_task(task_func=create_comment_relations,
                         task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise save_comment_on_object.retry(exc=spawned, countdown=5,
                                           max_retries=None)
    return spawned



@shared_task()
def create_comment_relations(current_pleb, comment, sb_object):
        res = comment_relations(current_pleb, comment, sb_object)

        if isinstance(res, Exception) is True:
            raise create_comment_relations.retry(exc=res, countdown=3,
                                                 max_retries=None)
        try:
            to_plebs = sb_object.owned_by.all()
        except CypherException:
            raise create_comment_relations.retry(exc=res, countdown=3,
                                                 max_retries=None)
        data = {'from_pleb': current_pleb, 'to_plebs': to_plebs,
                'sb_object': comment}
        spawned = spawn_task(task_func=spawn_notifications, task_param=data)
        if isinstance(spawned, Exception) is True:
            raise create_comment_relations.retry(exc=res, countdown=3,
                                                 max_retries=None)
        return True
