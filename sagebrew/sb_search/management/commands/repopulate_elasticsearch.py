from logging import getLogger

from django.core.management.base import BaseCommand

from neomodel import db

from plebs.neo_models import Pleb
from sb_questions.neo_models import Question
from sb_quests.neo_models import Quest
from sb_missions.neo_models import Mission
from sb_search.tasks import update_search_object

logger = getLogger('loggly_logs')


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates placeholder representatives.'

    def repopulate_elasticsearch(self):
        # Profiles
        skip = 0
        while True:
            query = 'MATCH (profile:Pleb) RETURN DISTINCT profile ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for profile in [Pleb.inflate(row[0]) for row in res]:
                update_search_object.apply_async(
                    kwargs={"object_uuid": profile.object_uuid,
                            "label": "pleb"})

        # Questions
        skip = 0
        while True:
            query = 'MATCH (question:Question) RETURN DISTINCT question ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for question in [Question.inflate(row[0]) for row in res]:
                update_search_object.apply_async(
                    kwargs={"object_uuid": question.object_uuid,
                            "label": "question"})

        # Quests
        skip = 0
        while True:
            query = 'MATCH (quest:Quest) RETURN DISTINCT quest ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for quest in [Quest.inflate(row[0]) for row in res]:
                update_search_object.apply_async(
                    kwargs={"object_uuid": quest.object_uuid,
                            "label": "quest"})
        # Missions
        skip = 0
        while True:
            query = 'MATCH (mission:Mission) RETURN DISTINCT mission ' \
                    'SKIP %s LIMIT 25' % skip
            skip += 24
            res, _ = db.cypher_query(query)
            if not res.one:
                break
            for mission in [Mission.inflate(row[0]) for row in res]:
                update_search_object.apply_async(
                    kwargs={"object_uuid": mission.object_uuid,
                            "label": "mission"})

    def handle(self, *args, **options):
        self.repopulate_elasticsearch()
        logger.info("Completed elasticsearch repopulation")
