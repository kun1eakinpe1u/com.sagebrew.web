from django.utils.text import slugify
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from py2neo.cypher.error import ClientError
from neomodel import db, CypherException, DoesNotExist

from sb_registration.utils import (verify_completed_registration)
from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer
from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer


def mission_list(request):
    serializer_data = []
    return render(request, 'mission_list.html', serializer_data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def select_mission(request):
    return render(request, 'mission_selector.html')


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def public_office_mission(request):
    return render(request, 'public_office_mission.html')


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def advocate_mission(request):
    return render(request, 'advocate_mission.html')


def mission_redirect_page(request, object_uuid=None):
    try:
        mission_obj = Mission.get(object_uuid)
    except (Mission.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, ClientError, IOError):
        return redirect("500_Error")

    return redirect("mission", object_uuid=object_uuid,
                    slug=slugify(mission_obj.get_mission_title()),
                    permanent=True)


def mission(request, object_uuid, slug=None):
    try:
        mission_obj = Mission.get(object_uuid)
    except (Mission.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, ClientError, IOError):
        return redirect("500_Error")
    mission_dict = MissionSerializer(mission_obj).data
    mission_dict['slug'] = slugify(mission_obj.get_mission_title())
    return render(request, 'mission.html', {
        "mission": mission_dict,
        "quest": QuestSerializer(Quest.get(mission_obj.owner_username)).data
    })


def mission_updates(request, object_uuid, slug=None):
    query = 'MATCH (quest:Quest)-[:EMBARKS_ON]->' \
            '(mission:Mission {object_uuid: "%s"})' \
            'RETURN quest' % object_uuid

    quest_res, _ = db.cypher_query(query)
    # Only need to check that at least one update exists here to mark that
    # updates are available for this mission.
    query = 'MATCH (mission:Mission {object_uuid: "%s"})<-[:ABOUT]-' \
            '(updates:Update) RETURN updates LIMIT 1' % object_uuid
    res, _ = db.cypher_query(query)
    if quest_res.one is None:
        return redirect("404_Error")
    # Instead of doing inflation and serialization of all the updates here
    # without pagination lets just indicate if we have any or not and then
    # hit the endpoint to gather the actual updates.
    if res.one:
        updates = True
    else:
        updates = False
    try:
        mission_obj = Mission.get(object_uuid)
    except (Mission.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, ClientError, IOError):
        return redirect("500_Error")
    quest = Quest.inflate(quest_res.one)
    return render(request, 'mission_updates.html',
                  {"updates": updates,
                   "mission": MissionSerializer(mission_obj).data,
                   "slug": slugify(mission_obj.get_mission_title()),
                   "quest": QuestSerializer(quest).data})


class LoginRequiredMixin(View):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class MissionSettingsView(LoginRequiredMixin):
    template_name = 'manage/mission_settings.html'

    @method_decorator(user_passes_test(
        verify_completed_registration,
        login_url='/registration/profile_information'))
    def dispatch(self, *args, **kwargs):
        return super(MissionSettingsView, self).dispatch(*args, **kwargs)

    def get(self, request, object_uuid=None, slug=None):
        query = 'MATCH (pleb:Pleb {username: "%s"})-[:IS_WAGING]->' \
            '(quest:Quest)-[:EMBARKS_ON]->(missions:Mission) ' \
            'RETURN missions, quest ' \
            'ORDER BY missions.created DESC' % request.user.username
        res, _ = db.cypher_query(query)
        if res.one is None:
            return redirect("select_mission")
        if object_uuid is None:
            # TODO handle if there aren't any missions yet
            mission_obj = Mission.inflate(res[0].missions)
            return redirect('mission_settings',
                            object_uuid=mission_obj.object_uuid,
                            slug=slugify(mission_obj.get_mission_title()))

        mission_obj = Mission.get(object_uuid)
        missions = [MissionSerializer(Mission.inflate(row.missions)).data
                    for row in res]
        quest = Quest.inflate(res.one.quest)
        return render(request, self.template_name, {
            "missions": missions,
            "mission": MissionSerializer(mission_obj).data,
            "quest": QuestSerializer(quest).data,
            "slug": slugify(mission_obj.get_mission_title())
        })
