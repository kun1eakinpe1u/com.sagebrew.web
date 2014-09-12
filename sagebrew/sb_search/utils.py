import traceback
import logging
from operator import itemgetter
from django.conf import settings
from django.template.loader import render_to_string

from elasticsearch import Elasticsearch

from api.utils import spawn_task
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion


logger = logging.getLogger('loggly_logs')


def update_search_index_doc_script(document_id, index, field, update_value, document_type):
    '''
    This can be used if you want to update a doc in an elasticsearch index
    using a script instead of using the .update functionality provided by
    the Elasticsearch package. This may be quicker and require future testing.

    :param document_id:
    :param index:
    :param field:
    :param update_value:
    :param document_type:
    :return:
    '''
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    body = {
        "script": {
            "script" : "ctx._source."+field+ " += update_value",
            "params" : {
                "update_value" : update_value
            }
        }
    }
    res = es.update(index=index, fields=["_source"], doc_type=document_type, id=document_id, body=body)
    return True

def update_search_index_doc(document_id, index, field, update_value,
                            document_type):
    '''
    This function can be used to update an existing document in an elasticsearch
    index. This function uses the .update functionality provided by the
    Elasticsearch python package but is also doable by using the script
    language for elasticsearch.

    :param document_id:
    :param index:
    :param field:
    :param update_value:
    :param document_type:
    :return:
    '''
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
    body = {
        "doc" : {
            field : update_value
        }
    }
    res = es.update(index=index, fields=["_source"], doc_type=document_type,
                    id=document_id, body=body)
    return True

def process_search_result(item):
    '''
    This util is called to process the search results returned from
    elasticsearch and render them to a hidden <div> element. The hidden
    div element is then accessed by javascript which uses the data in the
    element to create the div which will be displayed to users.

    :param item:
    :return:
    '''
    from sb_search.tasks import update_weight_relationship

    if 'sb_score' not in item['_source']:
            item['_source']['sb_score'] = 0
    if item['_type'] == 'question':
        spawn_task(update_weight_relationship,
                   task_param=
                   {'index': item['_index'],
                    'document_id': item['_id'],
                    'object_uuid': item['_source']['question_uuid'],
                    'object_type': 'question',
                    'current_pleb': item['_source']['related_user'],
                    'modifier_type': 'seen'})
        return {"question_uuid": item['_source']['question_uuid'],
                       "type": "question",
                       "temp_score": item['_score']*item['_source']['sb_score'],
                       "score": item['_score']}
    if item['_type'] == 'pleb':
        spawn_task(update_weight_relationship,
                   task_param={'index': item['_index'],
                               'document_id': item['_id'],
                               'object_uuid':
                                   item['_source']['pleb_email'],
                               'object_type': 'pleb',
                               'current_pleb': item['_source']['related_user'],
                               'modifier_type': 'seen'})
        return {"pleb_email": item['_source']['pleb_email'],
                       "type": "pleb",
                       "temp_score": item['_score']*item['_source']['sb_score'],
                       "score": item['_score']}