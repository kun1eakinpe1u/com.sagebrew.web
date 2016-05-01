from django.views.generic import View
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from py2neo.cypher import ClientError
from neomodel import DoesNotExist, CypherException, db

from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer


def quest(request, username):
    try:
        quest_obj = Quest.get(owner_username=username)
    except (CypherException, IOError, Quest.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    serializer_data = {
        "quest": QuestSerializer(quest_obj, context={'request': request}).data,
        "keywords": "Politics, Fundraising, Campaign, Quest, Activism"
    }
    if serializer_data['quest']['about'] is not None:
        serializer_data['description'] = serializer_data['quest']['about']
    else:
        serializer_data['description'] = "%s %s's Policies, Agenda, " \
                                         "and Platform." % (
                                             serializer_data['quest'][
                                                 'first_name'],
                                             serializer_data['quest'][
                                                 'last_name'])
    return render(request, 'quest.html', serializer_data)


class LoginRequiredMixin(View):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class QuestSettingsView(LoginRequiredMixin):
    template_name = 'manage/quest_settings.html'

    def get(self, request, username=None):
        from sb_missions.neo_models import Mission
        from plebs.neo_models import Address
        query = 'MATCH (person:Pleb {username: "%s"})' \
            '-[r:IS_WAGING]->(quest:Quest) WITH quest ' \
            'OPTIONAL MATCH (quest)-[:EMBARKS_ON]->(missions:Mission) ' \
            'RETURN quest, missions ORDER BY missions.created DESC' % (
                request.user.username)
        try:
            res, _ = db.cypher_query(query)
            if res.one is None:
                return redirect("404_Error")
        except(CypherException, ClientError):
            return redirect("500_Error")
        res.one.quest.pull()
        quest_obj = Quest.inflate(res.one.quest)
        quest_ser = QuestSerializer(quest_obj,
                                    context={'request': request}).data
        quest_ser['account_type'] = quest_obj.account_type
        if res.one.missions is None:
            mission_link = reverse('select_mission')
            mission_active = False
        else:
            mission_obj = Mission.inflate(res[0].missions)
            mission_link = reverse(
                'mission_settings',
                kwargs={"object_uuid": mission_obj.object_uuid,
                        "slug": slugify(mission_obj.get_mission_title())})
            mission_active = mission_obj.active
        res, _ = db.cypher_query('MATCH (a:Quest {owner_username: "%s"})'
                                 '-[:LOCATED_AT]->(b:Address) '
                                 'RETURN b' % quest_obj.owner_username)
        return render(request, self.template_name,
                      {"quest": quest_ser, "mission_link": mission_link,
                       "mission_active": mission_active,
                       "address": Address.inflate(res.one)})
