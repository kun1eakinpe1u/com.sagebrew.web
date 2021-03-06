import stripe
from uuid import uuid1
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db
from elasticsearch import Elasticsearch, TransportError

from sb_privileges.neo_models import SBAction, Privilege
from plebs.neo_models import Pleb, Address
from sb_registration.utils import create_user_util_test
from sb_locations.neo_models import Location
from sb_missions.neo_models import Mission
from sb_donations.neo_models import Donation
from sb_updates.neo_models import Update

from sb_quests.neo_models import Quest, Position
from sb_quests.serializers import QuestSerializer


class QuestEndpointTests(APITestCase):

    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        db.cypher_query(query)
        self.unit_under_test_name = 'quest'
        self.email = "success@simulator.amazonses.com"
        self.email2 = "bounce@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.pleb2 = create_user_util_test(self.email2)
        self.user = User.objects.get(email=self.email)
        self.user2 = User.objects.get(email=self.email2)
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        cache.clear()
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe.api_version = settings.STRIPE_API_VERSION

    def test_unauthorized(self):
        url = reverse('quest-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.post(url, data={}, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create(self):
        query = 'MATCH (a:Quest) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        position = Position(name="Senator").save()
        url = reverse('quest-list')
        data = {
            "about": "this is a test bio",
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        quest = Quest.nodes.get(owner_username=response.data['id'])
        self.assertEqual(quest.owner_username, self.user.username)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_with_tos(self):
        query = 'MATCH (a:Quest) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        position = Position(name="Senator").save()
        url = reverse('quest-list')
        data = {
            "about": "this is a test bio",
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "position": position.object_uuid,
            "tos_acceptance": True,
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        quest = Quest.nodes.get(owner_username=response.data['id'])
        self.assertTrue(quest.tos_acceptance)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_x_forwarded(self):
        query = 'MATCH (a:Quest) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        position = Position(name="Senator").save()
        url = reverse('quest-list')
        data = {
            "about": "this is a test bio",
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json',
                                    HTTP_X_FORWARDED_FOR="192.168.1.4")
        position.delete()
        quest = Quest.nodes.get(owner_username=response.data['id'])
        self.assertEqual(quest.owner_username, self.user.username)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_duplicate(self):
        query = 'MATCH (a:Quest) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        position = Position(name="Senator").save()
        url = reverse('quest-list')
        data = {
            "about": "this is a test bio",
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "position": position.object_uuid
        }
        self.client.post(url, data=data, format='json')
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'],
                         "You may only have one Quest!")

    def test_create_gain_intercom(self):
        self.client.force_authenticate(user=self.user)
        position = Position(name="Senator").save()
        try:
            action = SBAction.nodes.get(resource="intercom")
        except SBAction.DoesNotExist:
            action = SBAction(resource="intercom", permission="write").save()
        try:
            privilege = Privilege.nodes.get(name="quest")
        except Privilege.DoesNotExist:
            privilege = Privilege(name="quest").save()
        privilege.actions.connect(action)
        url = reverse('quest-list')
        data = {
            "about": "this is a test bio",
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "position": position.object_uuid
        }
        self.client.post(url, data=data, format='json')

        query = 'MATCH (a:Pleb {username:"%s"})-[:HAS]->(p:Privilege ' \
                '{name: "quest"})-[:GRANTS]->' \
                '(b:SBAction {resource: "intercom", permission: "write"}) ' \
                'RETURN b' % self.pleb.username
        res, _ = db.cypher_query(query)
        self.assertEqual(SBAction.inflate(res.one).resource, "intercom")
        action.delete()
        position.delete()
        privilege.delete()

    def test_create_gain_quest_privilege(self):
        self.client.force_authenticate(user=self.user)
        position = Position(name="Senator").save()
        action = SBAction(resource="intercom", permission="write").save()
        privilege = Privilege(name="quest").save()
        url = reverse('quest-list')
        data = {
            "about": "this is a test bio",
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "position": position.object_uuid
        }
        self.client.post(url, data=data, format='json')
        position.delete()
        query = 'MATCH (a:Pleb {username:"%s"})-[:HAS]->' \
                '(b:Privilege {name: "quest"}) RETURN b' % (
                    self.pleb.username)
        res, _ = db.cypher_query(query)
        action.delete()
        privilege.delete()
        self.assertEqual(Privilege.inflate(res.one).name, "quest")

    def test_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_fields_needed_human_readable(self):
        self.client.force_authenticate(user=self.user)
        self.quest.account_verification_fields_needed = \
            ['legal_entity.address.city', 'tos_acceptance.date']
        self.quest.save()
        cache.clear()
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)
        self.assertEqual(response.data['fields_needed_human_readable'],
                         'City,Terms of Service Acceptance Date')

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_no_quests(self):
        query = 'MATCH (a:Quest) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        stripe_res = stripe.Token.create(
            card={
                "exp_year": 2020,
                "exp_month": 0o2,
                "number": "4242424242424242",
                "currency": "usd",
                "cvc": 123,
                "name": "Test Test"
            }
        )
        customer = stripe.Customer.create(
            description="Customer for %s Quest" % self.quest.object_uuid,
            card=stripe_res['id'],
            email=self.pleb.email
        )
        account_token = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "Test Test",
                "routing_number": "110000000",
                "account_number": "000123456789",
                "account_holder_type": "company"
            }
        )
        account_res = stripe.Account.create(
            managed=True,
            country="US",
            email=self.pleb.email
        )
        account = stripe.Account.retrieve(account_res['id'])
        account.external_accounts.create(external_account=account_token['id'])
        sub = customer.subscriptions.create(plan='quest_premium')
        self.quest.stripe_customer_id = customer['id']
        self.quest.account_type = "paid"
        self.quest.stripe_subscription_id = sub['id']
        self.quest.stripe_id = account_res['id']
        self.quest.save()
        cache.clear()
        mission = Mission(title=str(uuid1())).save()
        self.quest.missions.connect(mission)
        update = Update().save()
        self.quest.updates.connect(update)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Quest.DoesNotExist):
            Quest.nodes.get(owner_username=self.pleb.username)
        with self.assertRaises(Mission.DoesNotExist):
            Mission.nodes.get(object_uuid=mission.object_uuid)
        with self.assertRaises(Update.DoesNotExist):
            Update.nodes.get(object_uuid=update.object_uuid)

    def test_update_take_quest_active(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        self.quest.active = False
        self.quest.save()
        cache.clear()
        data = {
            'active': True,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['active'], True)

    def test_update_take_quest_inactive(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        self.quest.active = True
        self.quest.save()
        cache.set("%s_quest" % self.quest.owner_username, self.quest)
        data = {
            'active': False,
        }
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        es.index(index='full-search-base', doc_type='quest',
                 id=self.quest.object_uuid,
                 body=QuestSerializer(self.quest).data)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['active'], False)
        try:
            es.get(index='full-search-base', doc_type='quest',
                   id=self.quest.object_uuid)
        except TransportError as e:
            self.assertEqual(e.info, {"_index": "full-search-base",
                                      "_type": "quest",
                                      "_id": self.quest.object_uuid,
                                      "found": False})

    def test_update_about(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "about": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['about'], data['about'])

    def test_update_about_too_long(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "about": "The first issues I encountered in my Quest was "
                     "with the short bio. The instructions in the text "
                     "box say there is a limit of 255 characters, but "
                     "another error comes up when I press submit that "
                     "says the limit is 150 characters. Just to text "
                     "things, I shortened it, this is waaaaay too long"
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update_facebook_fail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "facebook": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')
        self.assertIn('Enter a valid URL.', response.data['facebook'])

    def test_update_facebook_success(self):
        new_url = "http://www.facebook.com/johnnyapple"
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "facebook": new_url
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(new_url, response.data['facebook'])

    def test_update_linkedin_fail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "linkedin": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')
        self.assertIn('Enter a valid URL.', response.data['linkedin'])

    def test_update_linkedin_success(self):
        new_url = "https://www.linkedin.com/in/devonbleibtrey"
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "linkedin": new_url
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(new_url, response.data['linkedin'])

    def test_update_youtube_fail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "youtube": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')
        self.assertIn('Enter a valid URL.', response.data['youtube'])

    def test_update_youtube_success(self):
        new_url = "https://www.youtube.com/channel/UCCvhBF5Vfw05GOLdUYFATiQ"
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "youtube": new_url
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(new_url, response.data['youtube'])

    def test_update_twitter_fail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "twitter": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')
        self.assertIn('Enter a valid URL.', response.data['twitter'])

    def test_update_twitter_success(self):
        new_url = "https://twitter.com/devonbleibtrey"
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "twitter": new_url
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(new_url, response.data['twitter'])

    def test_update_website_fail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "website": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')
        self.assertIn('Enter a valid URL.', response.data['website'])

    def test_update_website_success(self):
        new_url = "https://www.sagebrew.com"
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "website": new_url
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(new_url, response.data['website'])

    def test_update_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "wallpaper_pic": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['wallpaper_pic'], data['wallpaper_pic'])

    def test_update_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "profile_pic": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['profile_pic'], data['profile_pic'])

    def test_update_address(self):
        self.client.force_authenticate(user=self.user)
        query = 'MATCH (a:Quest) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        position = Position(name="Senator").save()
        url = reverse('quest-list')
        data = {
            "about": "this is a test bio",
            "facebook": "https://www.facebook.com/devonbleibtrey",
            "linkedin": "https://www.linkedin.com/in/devonbleibtrey",
            "youtube": "https://www.youtube.com/"
                       "channel/UCCvhBF5Vfw05GOLdUYFATiQ",
            "twitter": "https://twitter.com/devonbleibtrey",
            "website": "https://www.sagebrew.com",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "address": {
                'city': "Walled Lake",
                'longitude': -83.48016,
                'state': "MI",
                'street': "300 Eagle Pond Dr.",
                'postal_code': "48390-3071",
                'congressional_district': "11",
                'latitude': 42.54083
            }
        }
        self.client.put(url, data=data, format='json')
        query = 'MATCH (a:Quest {object_uuid: "%s"})-[:LOCATED_AT]' \
                '->(b:Address) RETURN b' % response.data['id']
        res, _ = db.cypher_query(query)
        self.assertEqual(res.one['city'], "Walled Lake")

    def test_update_ssn_not_none(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "ssn": "000-00-0000"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_ssn_already_verified(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        address = Address(street="125 Glenwood Drive",
                          city="Walled Lake",
                          state="Michigan",
                          postal_code="48390",
                          country="USA",
                          county="Oakland",
                          congressional_district=11,
                          validated=True).save()
        self.quest.address.connect(address)
        stripe_res = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "Test Test",
                "routing_number": "110000000",
                "account_number": "000123456789",
                "account_holder_type": "company"
            }
        )
        data = {
            "stripe_token": stripe_res['id'],
            "ssn": "000000000",
            "ein": "000000000",
            "tos": True
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        stripe_res = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "Test Test",
                "routing_number": "110000000",
                "account_number": "000123456789",
                "account_holder_type": "company"
            }
        )
        data = {
            "stripe_token": stripe_res['id'],
            "ssn": "111111111",
            "ein": "000000000",
            "tos": True
        }
        response = self.client.put(url, data=data, format='json')

        self.assertIn("you can't change your Social Security Number after",
                      response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_title_not_none(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "title": " "
        }
        response = self.client.put(url, data=data, format='json')
        self.assertIsNone(response.data['title'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_with_tos(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        address = Address(street="125 Glenwood Drive",
                          city="Walled Lake",
                          state="Michigan",
                          postal_code="48390",
                          country="USA",
                          county="Oakland",
                          congressional_district=11,
                          validated=True).save()
        self.quest.address.connect(address)
        stripe_res = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "Test Test",
                "routing_number": "110000000",
                "account_number": "000123456789",
                "account_holder_type": "company"
            }
        )
        data = {
            "stripe_token": stripe_res['id'],
            "ssn": "000000000",
            "ein": "000000000",
            "tos": True
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_already_set_tos(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        address = Address(street="125 Glenwood Drive",
                          city="Walled Lake",
                          state="Michigan",
                          postal_code="48390",
                          country="USA",
                          county="Oakland",
                          congressional_district=11,
                          validated=True).save()
        self.quest.address.connect(address)
        self.quest.tos_acceptance = True
        self.quest.save()
        stripe_res = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "Test Test",
                "routing_number": "110000000",
                "account_number": "000123456789",
                "account_holder_type": "company"
            }
        )
        data = {
            "stripe_token": stripe_res['id'],
            "ssn": "000000000",
            "ein": "000000000",
            "tos": True
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_with_x_forwarded(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        address = Address(street="125 Glenwood Drive",
                          city="Walled Lake",
                          state="Michigan",
                          postal_code="48390",
                          country="USA",
                          county="Oakland",
                          congressional_district=11,
                          validated=True).save()
        self.quest.address.connect(address)
        stripe_res = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "Test Test",
                "routing_number": "110000000",
                "account_number": "000123456789",
                "account_holder_type": "company"
            }
        )
        data = {
            "stripe_token": stripe_res['id'],
            "ssn": "000000000",
            "ein": "000000000"
        }
        response = self.client.put(url, data=data, format='json',
                                   HTTP_X_FORWARDED_FOR="192.168.1.4")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_customer_token(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        stripe_res = stripe.Token.create(
            card={
                "exp_year": 2020,
                "exp_month": 0o2,
                "number": "4242424242424242",
                "currency": "usd",
                "cvc": 123,
                "name": "Test Test"
            }
        )
        data = {
            "customer_token": stripe_res['id']
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertIsNotNone(quest.stripe_customer_id)

    def test_update_customer_token_exists(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        stripe_res = stripe.Token.create(
            card={
                "exp_year": 2020,
                "exp_month": 0o2,
                "number": "4242424242424242",
                "currency": "usd",
                "cvc": 123,
                "name": "Test Test"
            }
        )
        customer = stripe.Customer.create(
            description="Customer for %s Quest" % self.quest.object_uuid,
            card=stripe_res['id'],
            email=self.pleb.email
        )
        stripe_res = stripe.Token.create(
            card={
                "exp_year": 2020,
                "exp_month": 0o2,
                "number": "4242424242424242",
                "currency": "usd",
                "cvc": 123,
                "name": "Test Test"
            }
        )
        self.quest.stripe_customer_id = customer['id']
        self.quest.save()
        data = {
            "customer_token": stripe_res['id']
        }
        response = self.client.put(url, data=data, format='json')
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertIsNotNone(quest.stripe_customer_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_promotion(self):
        settings.PRO_QUEST_END_DATE = datetime.now() + timedelta(days=1)
        self.client.force_authenticate(user=self.user)
        self.quest.stripe_subscription_id = None
        self.quest.account_type = "free"
        self.quest.save()
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "account_type": "promotion",
            "promotion_key": settings.PROMOTION_KEYS[0]
        }
        response = self.client.patch(url, data=data, format='json')
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertIsNotNone(quest.stripe_subscription_id)
        self.assertEqual(quest.account_type, "promotion")
        self.assertEqual(quest.application_fee, 0.021)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer = stripe.Customer.retrieve(quest.stripe_customer_id)
        customer.delete()
        settings.PRO_QUEST_END_DATE = datetime(2016, 11, 9)

    def test_update_promotion_customer_not_none(self):
        settings.PRO_QUEST_END_DATE = datetime.now() + timedelta(days=1)
        self.client.force_authenticate(user=self.user)
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        stripe_res = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "Test Test",
                "routing_number": "110000000",
                "account_number": "000123456789",
                "account_holder_type": "company"
            }
        )
        data = {
            "customer_token": stripe_res['id'],
            "account_type": "free"
        }
        self.client.put(url, data=data, format='json')
        data = {
            "account_type": "promotion",
            "promotion_key": settings.PROMOTION_KEYS[0]
        }
        response = self.client.patch(url, data=data, format='json')
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertIsNotNone(quest.stripe_subscription_id)
        self.assertEqual(quest.account_type, "promotion")
        self.assertEqual(quest.application_fee, 0.021)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer = stripe.Customer.retrieve(quest.stripe_customer_id)
        customer.delete()
        settings.PRO_QUEST_END_DATE = datetime(2016, 11, 9)

    def test_update_bad_promotion_key(self):
        self.client.force_authenticate(user=self.user)
        self.quest.stripe_subscription_id = None
        self.quest.account_type = "free"
        self.quest.save()
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "account_type": "promotion",
            "promotion_key": "my bad promotion key"
        }
        response = self.client.patch(url, data=data, format='json')
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertIsNone(quest.stripe_subscription_id)
        self.assertEqual(quest.account_type, "free")
        self.assertEqual(quest.application_fee, 0.021)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer = stripe.Customer.retrieve(quest.stripe_customer_id)
        customer.delete()

    def test_update_past_promotion_date(self):
        self.client.force_authenticate(user=self.user)
        self.quest.stripe_subscription_id = None
        self.quest.account_type = "free"
        self.quest.save()
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "account_type": "promotion",
            "promotion_key": settings.PROMOTION_KEYS[0]
        }
        previous_datetime = settings.PRO_QUEST_END_DATE
        settings.PRO_QUEST_END_DATE = datetime(2014, 6, 16)
        response = self.client.patch(url, data=data, format='json')
        settings.PRO_QUEST_END_DATE = previous_datetime
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        customer = stripe.Customer.retrieve(quest.stripe_customer_id)
        customer.delete()
        self.assertIsNone(quest.stripe_subscription_id)
        self.assertEqual(quest.account_type, "free")
        self.assertEqual(quest.application_fee, 0.021)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_paid(self):
        self.client.force_authenticate(user=self.user)
        self.quest.stripe_subscription_id = None
        self.quest.account_type = "free"
        self.quest.save()
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        stripe_res = stripe.Token.create(
            card={
                "exp_year": 2020,
                "exp_month": 0o2,
                "number": "4242424242424242",
                "currency": "usd",
                "cvc": 123,
                "name": "Test Test"
            }
        )
        data = {
            "customer_token": stripe_res['id'],
            "account_type": "paid"
        }
        response = self.client.patch(url, data=data, format='json')
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertIsNotNone(quest.stripe_subscription_id)
        self.assertEqual(quest.account_type, "paid")
        self.assertEqual(quest.application_fee, 0.021)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer = stripe.Customer.retrieve(quest.stripe_customer_id)
        customer.delete()

    def test_update_paid_to_free(self):
        self.client.force_authenticate(user=self.user)
        self.quest.stripe_subscription_id = None
        self.quest.account_type = "free"
        self.quest.save()
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        stripe_res = stripe.Token.create(
            card={
                "exp_year": 2020,
                "exp_month": 0o2,
                "number": "4242424242424242",
                "currency": "usd",
                "cvc": 123,
                "name": "Test Test"
            }
        )
        data = {
            "customer_token": stripe_res['id'],
            "account_type": "paid"
        }
        self.client.patch(url, data=data, format='json')
        data = {
            "account_type": "free"
        }
        response = self.client.patch(url, data=data, format='json')
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertIsNone(quest.stripe_subscription_id)
        self.assertEqual(quest.account_type, "free")
        self.assertEqual(quest.application_fee, 0.021)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer = stripe.Customer.retrieve(quest.stripe_customer_id)
        customer.delete()

    def test_update_free(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        stripe_res = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "Test Test",
                "routing_number": "110000000",
                "account_number": "000123456789",
                "account_holder_type": "company"
            }
        )
        data = {
            "customer_token": stripe_res['id'],
            "account_type": "free"
        }
        response = self.client.put(url, data=data, format='json')
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertIsNone(quest.stripe_subscription_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(quest.account_type, "free")
        self.assertEqual(quest.application_fee, 0.021)
        customer = stripe.Customer.retrieve(quest.stripe_customer_id)
        customer.delete()

    def test_update_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "title": "This is a fake title that a non owner set"
        }
        response = self.client.put(url, data=data, format='json')
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(quest.title, self.quest.title)
        self.assertEqual(response.data, ['Only the owner can edit this'])

    def test_stripe_token(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        address = Address(street="125 Glenwood Drive",
                          city="Walled Lake",
                          state="Michigan",
                          postal_code="48390",
                          country="USA",
                          county="Oakland",
                          congressional_district=11,
                          validated=True).save()
        self.quest.address.connect(address)
        stripe_res = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "Test Test",
                "routing_number": "110000000",
                "account_number": "000123456789",
                "account_holder_type": "company"
            }
        )
        data = {
            "stripe_token": stripe_res['id'],
            "ssn": "000000000",
            "ein": "000000000"
        }
        response = self.client.put(url, data=data, format='json')
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertEqual(quest.last_four_soc, "0000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stripe_token_no_ein(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        address = Address(street="125 Glenwood Drive",
                          city="Walled Lake",
                          state="Michigan",
                          postal_code="48390",
                          country="USA",
                          county="Oakland",
                          congressional_district=11,
                          validated=True).save()
        self.quest.address.connect(address)
        stripe_res = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "Test Test",
                "routing_number": "110000000",
                "account_number": "000123456789",
                "account_holder_type": "company"
            }
        )
        data = {
            "stripe_token": stripe_res['id'],
            "ssn": "000000000"
        }
        response = self.client.put(url, data=data, format='json')
        quest = Quest.nodes.get(object_uuid=self.quest.object_uuid)
        self.assertEqual(quest.last_four_soc, "0000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_moderators(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        url = reverse('quest-moderators',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ['test_test'])

    def test_moderators_unauthorized(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('quest-moderators',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)

        self.assertEqual(response.data['detail'], "You do not have permission "
                                                  "to perform this action.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_moderators(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-remove-moderators',
                      kwargs={'owner_username': self.quest.owner_username})
        new_pleb = Pleb(username=str(uuid1())).save()
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.put(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully removed '
                                                  'specified moderators '
                                                  'from your quest.')

    def test_add_moderators(self):
        self.client.force_authenticate(user=self.user)
        new_pleb = Pleb(username=str(uuid1())).save()
        url = reverse('quest-add-moderators',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully added '
                                                  'specified users to '
                                                  'your quest moderators.')

    def test_editors(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-editors',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ['test_test'])

    def test_editors_unauthorized(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('quest-editors',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)
        self.assertEqual(response.data['detail'], "You do not have permission "
                                                  "to perform this action.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_editors(self):
        self.client.force_authenticate(user=self.user)
        new_pleb = Pleb(username=str(uuid1())).save()
        url = reverse('quest-remove-editors',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.put(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully removed '
                                                  'specified editors '
                                                  'from your quest.')

    def test_add_editors(self):
        self.client.force_authenticate(user=self.user)
        new_pleb = Pleb(username=str(uuid1())).save()
        url = reverse('quest-add-editors',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.put(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully added '
                                                  'specified users '
                                                  'to your quest.')

    def test_missions(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username,
                          active=False).save()
        self.quest.missions.connect(mission)
        url = reverse('quest-missions',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)
        self.assertContains(response, mission.object_uuid,
                            status_code=status.HTTP_200_OK)

    def test_mission_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username,
                          active=False).save()
        self.quest.missions.connect(mission)
        url = reverse('quest-missions',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)
        self.assertNotContains(response, mission.object_uuid,
                               status_code=status.HTTP_200_OK)

    def test_donation_data(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(title=str(uuid1()),
                          owner_username=self.pleb.username).save()
        self.quest.missions.connect(mission)
        donation = Donation(amount=100,
                            owner_username=self.pleb.username).save()
        donation.mission.connect(mission)
        donation.owned_by.connect(self.pleb)
        url = reverse('quest-donation-data',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_follow(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-follow',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_already_follow(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-follow',
                      kwargs={'owner_username': self.quest.owner_username})
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.data['detail'], "Already following user.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unfollow(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-follow',
                      kwargs={'owner_username': self.quest.owner_username})
        self.client.post(url)
        url = reverse('quest-unfollow',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_already_unfollow(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-unfollow',
                      kwargs={'owner_username': self.quest.owner_username})
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.data['detail'], "Already not following user.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-list',
                      kwargs={'object_uuid': self.quest.owner_username}) + \
            "?about_type=quest"
        self.quest.moderators.connect(self.pleb)
        self.quest.editors.connect(self.pleb)
        cache.clear()
        data = {
            'title': str(uuid1()),
            'content': str(uuid1()),
            'about_type': 'quest',
            'about_id': self.quest.owner_username
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['title'], response.data['title'])

    def test_endorsements(self):
        mission = Mission(owner_username=self.pleb.username).save()
        self.quest.missions.connect(mission)
        mission.quest_endorsements.connect(self.quest)
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-endorsed',
                      kwargs={'owner_username': self.pleb.username})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(mission.object_uuid, res.data['results'][0]['id'])


class PositionEndpointTests(APITestCase):

    def setUp(self):
        self.unit_under_test_name = 'position'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.mission = Mission(owner_username=self.quest.owner_username,
                               focus_on_type="position").save()
        self.quest.owner.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        self.quest.editors.connect(self.pleb)
        self.position = Position(name="Senator").save()
        self.mission.position.connect(self.position)
        query = 'MATCH (a:Location) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        self.location = Location(name="Michigan").save()
        cache.clear()

    def test_unauthorized(self):
        url = reverse('position-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.post(url, data={}, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_detail_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['name'], 'Senator')

    def test_detail_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['href'], self.url + url)

    def test_detail_location(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['location'])

    def test_detail_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['type'], 'position')

    def test_detail_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['id'], self.position.object_uuid)

    def test_put(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.put(url, {'name': 'House Rep'}, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.patch(url, {'name': 'House Rep'}, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_non_admin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-add')
        response = self.client.post(url, {
            "name": "Council Member",
            "location_name": "Michigan",
            "location_uuid": "",
            "level": "state"
        }, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_add_anon(self):
        url = reverse('position-add')
        response = self.client.post(url, {
            "name": "Council Member",
            "location_name": "Michigan",
            "location_uuid": "",
            "level": "local"
        }, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_add_admin(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('position-add')
        response = self.client.post(url, {
            "name": "Mayor",
            "location_name": self.location.name,
            "location_uuid": "",
            "level": "local"
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mayor')
        self.assertEqual(response.data['location'], self.location.object_uuid)

    def test_add_get(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('position-add')
        response = self.client.get(url)
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_add_uuid(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('position-add')
        response = self.client.post(url, {
            "name": "Governor",
            "location_name": "",
            "location_uuid": self.location.object_uuid,
            "level": "state"
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Governor')

    def test_add_invalid_serializer(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('position-add')
        response = self.client.post(url, {
            "name": "Delegate",
            "location_uuid": self.location.object_uuid
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_council_update(self):
        try:
            user = User.objects.get(username="tyler_wiersing")
            self.client.force_authenticate(user=user)
        except User.DoesNotExist:
            self.user.username = 'tyler_wiersing'
            self.user.save()
            self.client.force_authenticate(user=self.user)
        self.pleb.username = 'tyler_wiersing'
        self.pleb.save()
        cache.clear()
        position = Position(verified=False, name="Test Update").save()

        url = reverse('position-council-update',
                      kwargs={'object_uuid': position.object_uuid})
        res = self.client.put(url, data={'verified': True, 'name': "New Name"},
                              format='json')
        position.delete()
        self.pleb.username = 'test_test'
        self.pleb.save()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], 'New Name')
        self.assertTrue(res.data['verified'])

    def test_council_serializer_errors(self):
        try:
            user = User.objects.get(username="tyler_wiersing")
            self.client.force_authenticate(user=user)
        except User.DoesNotExist:
            self.user.username = 'tyler_wiersing'
            self.user.save()
            self.client.force_authenticate(user=self.user)
        self.pleb.username = 'tyler_wiersing'
        self.pleb.save()
        cache.clear()
        position = Position(verified=False, name="Test Update").save()

        url = reverse('position-council-update',
                      kwargs={'object_uuid': position.object_uuid})
        res = self.client.put(url, data={'verified': "hello"},
                              format='json')
        position.delete()
        self.pleb.username = 'test_test'
        self.pleb.save()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['verified'],
                         ["\"hello\" is not a valid boolean."])

    def test_council_update_unauthorized(self):
        cache.clear()
        position = Position(verified=False, name="Test Update").save()

        self.client.force_authenticate(user=self.user)
        url = reverse('position-council-update',
                      kwargs={'object_uuid': position.object_uuid})
        res = self.client.put(url, data={'verified': True, 'name': "New Name"},
                              format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        position.delete()

    def test_user_created(self):
        position = Position(name="Some Random Test Name",
                            user_created=True).save()
        self.client.force_authenticate(user=self.user)
        url = reverse('position-user-created')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(position.object_uuid, res.data[0]['id'])
        position.delete()
