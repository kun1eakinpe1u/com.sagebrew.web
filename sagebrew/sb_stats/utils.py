from django.core.cache import cache

from neomodel import CypherException

from sb_questions.neo_models import Question


def update_view_count(sb_object):
    try:
        sb_object.increment_view_count()
        child_class = sb_object.get_child_label()
        if "Question" in child_class:
            question = Question.nodes.get(object_uuid=sb_object.object_uuid)
            cache.set(question.object_uuid, question)
    except(CypherException, IOError) as e:
        return e

    return sb_object
