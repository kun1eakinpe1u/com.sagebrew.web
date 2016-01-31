import pytz
import bleach
from uuid import uuid1
from datetime import datetime

from django.utils.text import slugify
from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from neomodel import db

from plebs.neo_models import Pleb
from sb_goals.neo_models import Goal
from api.utils import gather_request_data, spawn_task
from sb_base.serializers import TitledContentSerializer
from sb_notifications.tasks import spawn_notifications

from .neo_models import Update


class UpdateSerializer(TitledContentSerializer):
    title = serializers.CharField(min_length=5, max_length=140)
    goals = serializers.SerializerMethodField()
    about_type = serializers.ChoiceField(choices=[
        ('mission', "Mission"), ('quest', "Quest"), ('seat', "Seat"),
        ('goal', "Goal")])
    about_id = serializers.CharField(min_length=2, max_length=36)
    about = serializers.SerializerMethodField()

    def create(self, validated_data):
        # TODO we don't have a way currently to distinguish what a Update is
        # about. Think it'll be based on an attribute submitted by the front
        # end. That will be based on where it's at (make update from Public
        # Office Mission vs Advocate Mission vs Quest vs etc)
        request, _, _, _, _ = gather_request_data(self.context)
        quest = validated_data.pop('quest', None)

        validated_data['content'] = bleach.clean(validated_data.get(
            'content', ""))
        owner = Pleb.get(request.user.username)
        validated_data['owner_username'] = owner.username
        about = validated_data.pop('about', None)
        about_type = validated_data.get('about_type')
        update = Update(**validated_data).save()
        quest.updates.connect(update)
        if validated_data.get('about_type') == "goal":
            query = 'MATCH (c:Quest {object_uuid:"%s"})-[:EMBARKS_ON]->' \
                    '(mission:Mission)-[:WORKING_TOWARDS]->' \
                    '(g:Goal {title:"%s"}) ' \
                    'RETURN g' % (quest.object_uuid,
                                  validated_data.get('about_id'))
            res, _ = db.cypher_query(query)
            goal = Goal.inflate(res.one)
            update.goals.connect(goal)
            goal.updates.connect(update)
        # moved url generation into the if because we currently don't have a
        # way to view just a quests updates
        # TODO view quest updates only
        url = ""
        if about_type == 'mission':
            update.mission.connect(about)
            url = reverse('mission_updates',
                          kwargs={'object_uuid': about.object_uuid,
                                  'slug': slugify(about.get_mission_title())})
        elif about_type == 'quest':
            update.quest.connect(about)
        cache.delete("%s_updates" % quest.object_uuid)
        task_params = {
            "sb_object": update.object_uuid,
            "to_plebs": quest.get_followers(),
            "from_pleb": request.user.username,
            "notification_id": str(uuid1()),
            "url": url,
            "action_name": "%s %s has made an Update on a Quest you follow!" %
                           (request.user.first_name, request.user.last_name),
            "public": True
        }
        spawn_task(task_func=spawn_notifications, task_param=task_params)
        return update

    def update(self, instance, validated_data):
        instance.title = validated_data.pop('title', instance.title)
        instance.content = validated_data.pop('content', instance.content)
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()
        return instance

    def get_goals(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return Update.get_goals(obj.object_uuid)

    def get_url(self, obj):
        # removed this currently because this view doesn't exist
        # TODO create view to display quest updates
        """
        elif obj.about_type == "quest":
            about = Quest.get(obj.about_id)
            return reverse('quest_updates',
                           kwargs={'object_uuid': about.owner_username},
                           request=request)
        """
        from sb_missions.neo_models import Mission
        request, _, _, _, _ = gather_request_data(self.context)
        if obj.about_type == "mission":
            about = Mission.get(obj.about_id)
            return reverse('mission_updates',
                           kwargs={'object_uuid': about.object_uuid,
                                   'slug': slugify(about.get_mission_title())},
                           request=request)
        else:
            return None

    def get_href(self, obj):
        request, _, _, _, _ = gather_request_data(
            self.context,
            expedite_param=self.context.get('expedite_param', None),
            expand_param=self.context.get('expand_param', None))
        return reverse(
            'update-detail', kwargs={'object_uuid': obj.object_uuid},
            request=request)

    def get_about(self, obj):
        from sb_missions.neo_models import Mission
        from sb_missions.serializers import MissionSerializer
        from sb_quests.neo_models import Quest
        from sb_quests.serializers import QuestSerializer
        if obj.about_type == "mission":
            return MissionSerializer(Mission.get(obj.about_id)).data
        elif obj.about_type == "quest":
            return QuestSerializer(Quest.get(obj.about_id)).data
        else:
            return None
