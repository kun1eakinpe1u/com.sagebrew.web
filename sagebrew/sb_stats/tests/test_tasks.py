from uuid import uuid1
import time

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test

from sb_stats.tasks import update_view_count_task


class TestUpdateViewCountTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(title=str(uuid1())).save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_update_view_count_task(self):
        data = {
            "username": self.pleb.username,
            "object_uuid": self.question.object_uuid
        }
        res = update_view_count_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_update_view_count_task_already_connected(self):
        self.question.viewed_by.connect(self.pleb)
        self.pleb.viewed.connect(self.question)
        data = {
            "username": self.pleb.username,
            "object_uuid": self.question.object_uuid
        }
        res = update_view_count_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
