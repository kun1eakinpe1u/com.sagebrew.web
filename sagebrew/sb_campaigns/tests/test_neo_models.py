from uuid import uuid1

from django.test import TestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_donations.neo_models import Donation
from sb_goals.neo_models import Goal
from sb_campaigns.neo_models import Campaign


class TestCampaignNeoModel(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.email = "bounce@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.campaigner = Pleb.nodes.get(email=self.email)
        self.goal = Goal(title="This is my goal",
                         summary="Hey this is required",
                         pledged_vote_requirement=10, monetary_requirement=10)
        self.goal.save()
        self.donation = Donation(amount=5.0).save()

    def test_create_campaign(self):
        stripe_id = str(uuid1())
        campaign = Campaign(stripe_id=stripe_id).save()
        campaign.donations.connect(self.donation)
        self.donation.campaign.connect(campaign)
        campaign.goals.connect(self.goal)
        campaign.owned_by.connect(self.pleb)
        self.goal.campaign.connect(campaign)

        campaign_query = Campaign.nodes.get(stripe_id=stripe_id)
        self.assertEqual(campaign_query.stripe_id, stripe_id)
