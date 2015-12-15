from django.utils.text import slugify
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from py2neo.cypher.error import ClientError
from neomodel import db, CypherException, DoesNotExist

from sb_registration.utils import (verify_completed_registration)
from sb_updates.neo_models import Update
from sb_updates.serializers import UpdateSerializer
from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer


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
    if mission_obj.title:
        title = mission_obj.title
    else:
        if mission_obj.focus_name:
            title = mission_obj.focus_name.title().replace(
                    '-', ' ').replace('_', ' ')
        else:
            title = None
    return redirect("mission", object_uuid=object_uuid,
                    slug=slugify(title), permanent=True)


def mission(request, object_uuid, slug=None):
    try:
        mission_obj = Mission.get(object_uuid)
    except (Mission.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, ClientError, IOError):
        return redirect("500_Error")
    mission_dict = MissionSerializer(mission_obj).data
    mission_dict['slug'] = slug
    return render(request, 'mission.html', mission_dict)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def mission_settings(request):
    query = 'MATCH (pleb:Pleb {username: "%s"})-[:IS_WAGING]->' \
            '(quest:Quest)-[:EMBARKS_ON]->(missions:Mission) ' \
            'RETURN missions ' \
            'ORDER BY missions.created DESC' % request.user.username
    res, _ = db.cypher_query(query)
    if res.one is None:
        return redirect("404_Error")
    settings_info = {
        "missions": [MissionSerializer(Mission.inflate(row[0])).data
                     for row in res],
        "selected": MissionSerializer(Mission.inflate(res.one)).data
    }
    return render(request, 'manage/mission_settings.html', settings_info)


def mission_updates(request, object_uuid, slug=None):
    query = 'MATCH (updates:Update) RETURN updates'
    res, _ = db.cypher_query(query)
    try:
        mission_obj = Mission.get(object_uuid)
    except (Mission.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, ClientError, IOError):
        return redirect("500_Error")
    return render(request, 'mission_updates.html',
                  {"updates": [UpdateSerializer(
                          Update.inflate(row[0])).data for row in res],
                   "mission": MissionSerializer(mission_obj).data,
                   "slug": slug})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def edit_epic(request, object_uuid=None, slug=None):
    try:
        mission_obj = Mission.get(object_uuid=object_uuid)
    except (Mission.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, ClientError, IOError):
        return redirect("500_Error")
    return render(request, 'manage/edit_epic.html',
                  MissionSerializer(mission_obj).data)
