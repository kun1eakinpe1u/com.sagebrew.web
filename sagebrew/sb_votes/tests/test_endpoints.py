from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question


class VoteEndpointTests(APITestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        cache.clear()
        self.unit_under_test_name = 'goal'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.question = Question().save()

    def test_vote_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("question-detail",
                      kwargs={'object_uuid': self.question.object_uuid})
        res = self.client.get(url + "votes/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_vote_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "vote_type": True
        }
        url = reverse("question-detail",
                      kwargs={'object_uuid': self.question.object_uuid})
        res = self.client.post(url + "votes/", data=data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
