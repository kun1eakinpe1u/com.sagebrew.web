import pytz
import logging
from datetime import datetime

from django.conf import settings
from django.core.cache import cache

from celery import shared_task
from elasticsearch import Elasticsearch
from py2neo.cypher.error import ClientError
from neomodel import DoesNotExist, CypherException, db
from elasticsearch.exceptions import (ElasticsearchException, TransportError,
                                      ConflictError, RequestError)

from api.utils import spawn_task
from plebs.neo_models import Pleb
from sb_questions.neo_models import Question

from .neo_models import SearchQuery, KeyWord

logger = logging.getLogger('loggly_logs')


@shared_task()
def update_search_query(username, query_param, keywords):
    """
    This task creates a search query node then calls the task to create and
    attach keyword nodes to the search query node

    :param username:
    :param query_param:
    :param keywords:
    :return:
    """
    try:
        res, _ = db.cypher_query("MATCH (a:Pleb {username:'%s'}) RETURN a" %
                                 username)
        if res.one:
            res.one.pull()
            pleb = Pleb.inflate(res.one)
        else:
            raise update_search_query.retry(
                exc=DoesNotExist("Profile with username: "
                                 "%s does not exist" % username), countdown=3,
                max_retries=None)
    except (CypherException, IOError) as e:
        raise update_search_query.retry(exc=e, countdown=3, max_retries=None)
    try:
        search_query = SearchQuery.nodes.get(search_query=query_param)
        if pleb.searches.is_connected(search_query):
            rel = pleb.searches.relationship(search_query)
            rel.times_searched += 1
            rel.last_searched = datetime.now(pytz.utc)
            rel.save()
            return True
        else:
            rel = pleb.searches.connect(search_query)
            rel.save()
            search_query.searched_by.connect(pleb)
            return True
    except (SearchQuery.DoesNotExist, DoesNotExist):
        search_query = SearchQuery(search_query=query_param)
        search_query.save()
        search_query.searched_by.connect(pleb)
        rel = pleb.searches.connect(search_query)
        rel.save()
        for keyword in keywords:
            keyword['query_param'] = query_param
            spawned = spawn_task(task_func=create_keyword, task_param=keyword)
            if isinstance(spawned, Exception) is True:
                return spawned
        return True
    except (CypherException, IOError) as e:
        raise update_search_query.retry(exc=e, countdown=3, max_retries=None)
    except Exception as e:
        raise update_search_query.retry(exc=e, countdown=3, max_retries=None)


@shared_task()
def create_keyword(text, relevance, query_param):
    """
    This function takes

    :param text:
    :param relevance:
    :param query_param:
    :return:
    """
    try:
        try:
            search_query = SearchQuery.nodes.get(search_query=query_param)
        except (SearchQuery.DoesNotExist, DoesNotExist) as e:
            raise create_keyword.retry(exc=e, countdown=3, max_retries=None)
        try:
            keyword = KeyWord.nodes.get(keyword=text)
            rel = search_query.keywords.connect(keyword)
            rel.relevance = relevance
            rel.save()
            keyword.search_queries.connect(search_query)
            search_query.save()
            keyword.save()
            return True
        except (KeyWord.DoesNotExist, DoesNotExist):
            keyword = KeyWord(keyword=text).save()
            rel = search_query.keywords.connect(keyword)
            rel.relevance = relevance
            rel.save()
            keyword.search_queries.connect(search_query)
            search_query.save()
            keyword.save()
            return True
    except (CypherException, IOError, ClientError) as e:
        logger.exception("Cypher Exception: ")
        raise create_keyword.retry(exc=e, countdown=3, max_retries=None)


@shared_task()
def update_search_object(object_uuid, label=None, object_data=None,
                         index="full-search-base"):
    from plebs.serializers import PlebSerializerNeo
    from sb_quests.serializers import QuestSerializer
    from sb_quests.neo_models import Quest
    from sb_missions.serializers import MissionSerializer
    from sb_missions.neo_models import Mission
    from sb_questions.serializers import QuestionSerializerNeo
    from sb_base.neo_models import get_parent_votable_content
    if label is None:
        label = get_parent_votable_content(
            object_uuid).get_child_label().lower()
    logger.critical("Updating Search Object")
    logger.critical({"object_uuid": object_uuid})
    query = 'MATCH (a:%s {object_uuid:"%s"}) RETURN a' % \
            (label.title(), object_uuid)
    res, _ = db.cypher_query(query)
    if res.one:
        res.one.pull()
    else:
        raise update_search_object.retry(
            exc=DoesNotExist('Object with uuid: %s '
                             'does not exist' % object_uuid), countdown=3,
            max_retries=None)
    if label == "question":
        instance = Question.inflate(res.one)
        object_data = QuestionSerializerNeo(instance).data
        if 'mission' in object_data:
            object_data.pop('mission')
        if 'profile' in object_data:
            object_data.pop('profile')
        logger.critical(object_data)
    elif label == "quest":
        instance = Quest.inflate(res.one)
        object_data = QuestSerializer(instance).data
        logger.critical(object_data)
    elif label == "mission":
        instance = Mission.inflate(res.one)
        object_data = MissionSerializer(instance).data
        # Need to pop review_feedback because ES's serializer cannot parse
        # set types.
        # If we don't pop it we receive
        # TypeError("Unable to serialize set([]) (type: <type 'set'>)",))
        # If we can submit a JSON serialized version we can get around this by
        # using:
        # from rest_framework.renderers import JSONRenderer
        # JSONRenderer().render(serializer.data)
        # Also please note python's json.dumps() function runs into this same
        # issue.
        if 'review_feedback' in object_data:
            object_data.pop('review_feedback', None)
        if 'quest' in object_data:
            object_data.pop('quest')
        logger.critical(object_data)
    elif label == "pleb":
        instance = Pleb.inflate(res.one)
        object_data = PlebSerializerNeo(instance).data
        if 'quest' in object_data:
            object_data.pop('quest')
        logger.critical(object_data)
    else:
        # Currently we only need this functionality for Questions as
        # they are the only objects in search that we display votes
        # for in the search interface.
        error_dict = {
            "message": "Search False setup. "
                       "Object Data None, Instance not None",
            "instance_label": label,
            "instance_uuid": object_uuid,
        }
        logger.critical(error_dict)
        return False
    try:
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        res = es.index(index=index, doc_type=object_data['type'],
                       id=object_uuid, body=object_data)
    except (ElasticsearchException, TransportError,
            ConflictError, RequestError) as e:
        logger.exception("Failed to connect to Elasticsearch")
        logger.critical(object_data)
        raise update_search_object.retry(exc=e, countdown=5, max_retries=None)
    except KeyError:
        error_dict = {
            "message": "Search: KeyError False creation",
            "instance_uuid": object_uuid,
            "object_data": object_data
        }
        logger.critical(error_dict)
        return False
    try:
        if instance.search_id is None:
            instance.search_id = res['_id']
            instance.populated_es_index = True
            instance.save()
    except AttributeError:
        pass

    cache.delete("%s_vote_search_update" % object_uuid)
    return res
