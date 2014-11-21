from django.contrib.auth.models import User
from django.test import TestCase
from api.utils import wait_util

from sb_tag.utils import (create_tag_relations_util)
from sb_tag.neo_models import SBAutoTag
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util


class TestCreateTagRelations(TestCase):
    def setUp(self):
        self.tags = []
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        tag_list = ['these fake', 'are fake', 'fake fake', 'tags fake']
        for tag in tag_list:
            try:
                self.tags.append(SBAutoTag(tag_name=tag).save())
            except Exception:
                self.tags.append(SBAutoTag.nodes.get(tag_name=tag))

    def test_create_tag_relations_success(self):
        res = create_tag_relations_util(self.tags)

        self.assertTrue(res)

    def test_create_tag_relations_connected(self):
        tag1 = SBAutoTag(tag_name="amazing tag").save()
        tag2 = SBAutoTag(tag_name="another amazing tag").save()

        rel = tag1.frequently_auto_tagged_with.connect(tag2)
        rel.save()

        res = create_tag_relations_util([tag1, tag2])

        self.assertTrue(res)

    def test_create_tag_relations_empty(self):
        res = create_tag_relations_util([])
        self.assertFalse(res)

