import bleach

from django.core.cache import cache

from rest_framework import serializers
from rest_framework.reverse import reverse

from plebs.neo_models import Pleb
from sb_goals.neo_models import Goal
from api.utils import gather_request_data
from sb_campaigns.neo_models import Campaign
from sb_base.serializers import TitledContentSerializer

from .neo_models import Update



class UpdateSerializer(TitledContentSerializer):
    goals = serializers.SerializerMethodField()
    campaign = serializers.SerializerMethodField()

    def validate_title(self, value):
        return value

    def create(self, validated_data):
        request, _, _, _, _ = gather_request_data(self.context)
        campaign = validated_data.pop('campaign', None)
        print campaign
        validated_data['content'] = bleach.clean(validated_data.get(
            'content', ""))
        owner = Pleb.get(request.user.username)
        print owner
        validated_data['owner_username'] = owner.username
        update = Update(**validated_data).save()
        update.campaign.connect(campaign)
        campaign.updates.connect(update)
        update.owned_by.connect(owner)
        update_for = Goal.inflate(Campaign.get_current_target_goal(
            campaign.object_uuid))
        print update_for
        cache.set("%s_target_goal" % (campaign.object_uuid), update_for)
        update_for.updates.connect(update)
        update.goals.connect(update_for)
        return update

    def update(self, instance, validated_data):
        instance.title = validated_data.pop('title', instance.title)
        instance.content = validated_data.pop('content', instance.content)
        instance.save()
        return instance

    def get_goals(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return Update.get_goals(obj.object_uuid)


    def get_campaign(self, obj):
        request, _, _, relation, _ = gather_request_data(self.context)
        campaign = Update.get_campaign(obj.object_uuid)
        if campaign is not None:
            if relation == 'hyperlink':
                return reverse('campaign-detail',
                               kwargs={'object_uuid': campaign},
                               request=request)
        return campaign

    def get_url(self, obj):
        request, _, _, _, _ = gather_request_data(self.context)
        return reverse('update-detail',
                       kwargs={'object_uuid': obj.object_uuid},
                       request=request)
