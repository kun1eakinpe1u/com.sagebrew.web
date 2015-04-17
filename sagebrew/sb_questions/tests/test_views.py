from uuid import uuid1

from django.contrib.auth.models import User


from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework import status

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_questions.neo_models import Question


class TestGetQuestionSearchView(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.pleb.save()
        self.client.force_authenticate(user=self.user)

    def test_get_question_search_view_success(self):
        question = Question(object_uuid=str(uuid1()), content='test',
                            title='test title').save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/search/%s/' %
                              question.object_uuid)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
