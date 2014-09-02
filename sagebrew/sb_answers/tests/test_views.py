import time
from datetime import datetime
from uuid import uuid1
from base64 import b64encode
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from plebs.neo_models import Pleb
from sb_answers.views import (save_answer_view)

class TestSaveAnswerView(TestCase):
    def setUp(self):
        try:
            pleb = Pleb.index.get(email='tyler.wiersing@sagebrew.com')
            pleb.delete()
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@sagebrew.com')
        except Pleb.DoesNotExist:
            self.factory = APIRequestFactory()
            self.user = User.objects.create_user(
                username='Tyler', email='tyler.wiersing@sagebrew.com')

    def test_save_answer_view_correct_data(self):
        my_dict = {'content': 'test answer', 'current_pleb': self.user.email,
                   'question_uuid': '12312', 'to_pleb': self.user.email}

        request = self.factory.post('/answers/submit_answer_api/', data=my_dict,
                                    format='json')
        request.user = self.user

        response = save_answer_view(request)

        self.assertEqual(response.status_code, 200)

    def test_save_answer_view_missing_data(self):
        my_dict = {'current_pleb': self.user.email,
                   'question_uuid': '12312', 'to_pleb': self.user.email}

        request = self.factory.post('/answers/submit_answer_api/', data=my_dict,
                                    format='json')
        request.user = self.user

        response = save_answer_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_answer_view_int_data(self):
        my_dict = 98897965
        request = self.factory.post('/answers/submit_answer_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_answer_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_answer_view_string_data(self):
        my_dict = 'sdfasdfasdf'
        request = self.factory.post('/answers/submit_answer_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_answer_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_answer_view_list_data(self):
        my_dict = []
        request = self.factory.post('/answers/submit_answer_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_answer_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_answer_view_float_data(self):
        my_dict = 1.010101010
        request = self.factory.post('/answers/submit_answer_api/', data=my_dict,
                                    format='json')
        request.user = self.user
        response = save_answer_view(request)

        self.assertEqual(response.status_code, 400)

    def test_save_answer_view_image_data(self):
        with open(settings.PROJECT_DIR + "/sb_posts/" +
                  "tests/images/test_image.jpg", "rb") as image_file:
            image = b64encode(image_file.read())

        request = self.factory.post('/answers/submit_answer_api/', data=image,
                                    format='json')
        request.user = self.user
        response = save_answer_view(request)

        self.assertEqual(response.status_code, 400)