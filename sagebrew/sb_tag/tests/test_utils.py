from uuid import uuid1
from django.contrib.auth.models import User
from django.test import TestCase

from plebs.neo_models import Pleb

from sb_questions.neo_models import SBQuestion
from sb_tag.utils import (add_tag_util, add_auto_tags_util,
                          create_tag_relations)
from sb_tag.neo_models import SBAutoTag

class TestCreateTagUtil(TestCase):

    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

    def test_create_tag_util_success(self):
        question = SBQuestion(question_id=uuid1())
        question.save()
        tags = ['test','tag','please','do', 'not','fail','in', 'testing']
        res = add_tag_util(object_type='question',
                           object_uuid=question.question_id,
                           tags=tags)

        self.assertTrue(res)

    def test_create_tag_util_object_does_not_exist(self):
        tags = ['test','tag','please','do', 'not','fail','in', 'testing']
        res = add_tag_util(object_type='question',
                           object_uuid=uuid1(),
                           tags=tags)

        self.assertFalse(res)

    def test_create_tag_util_invalid_object(self):
        question = SBQuestion(question_id=uuid1())
        question.save()
        tags = ['test','tag','please','do', 'not','fail','in', 'testing']
        res = add_tag_util(object_type='nothing',
                           object_uuid=question.question_id,
                           tags=tags)

        self.assertFalse(res)

    def test_create_tag_util_empty_tags(self):
        question = SBQuestion(question_id=uuid1())
        question.save()
        tags = []
        res = add_tag_util(object_type='question',
                           object_uuid=question.question_id,
                           tags=tags)

        self.assertFalse(res)

class TestCreateAutoTagUtil(TestCase):

    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

    def test_create_auto_tag_util_success(self):
        question = SBQuestion(question_id=uuid1())
        question.save()
        util_dict = [{'object_type': 'question',
                      'object_uuid': question.question_id,
                      'tags': {'relevance': '.9', 'text': 'test'}}]
        res = add_auto_tags_util(util_dict)

        self.assertTrue(res)

    def test_create_auto_tag_util_object_does_not_exist(self):
        util_dict = [{'object_type': 'question',
                      'object_uuid': uuid1(),
                      'tags': {'relevance': '.9', 'text': 'test'}}]

        res = add_auto_tags_util(util_dict)

        self.assertFalse(res)

    def test_create_auto_tag_util_invalid_object(self):
        question = SBQuestion(question_id=uuid1())
        question.save()
        util_dict = [{'object_type': 'nothing',
                      'object_uuid': question.question_id,
                      'tags': {'relevance': '.9', 'text': 'test'}}]
        res = add_auto_tags_util(util_dict)

        self.assertFalse(res)

    def test_create_auto_tag_key_error(self):
        question = SBQuestion(question_id=uuid1())
        question.save()
        util_dict = [{'object_type': 'nothing',
                      'object_uuid': question.question_id}]
        res = add_auto_tags_util(util_dict)

        self.assertFalse(res)

class TestCreateAutoTagRelationships(TestCase):

    def setUp(self):
        self.email = 'devon@sagebrew.com'
        try:
            pleb = Pleb.index.get(email=self.email)
            wall = pleb.traverse('wall').run()[0]
            wall.delete()
            pleb.delete()
        except Pleb.DoesNotExist:
            pass

        self.user = User.objects.create_user(
            username='Tyler' + str(uuid1())[:25], email=self.email)
        self.pleb = Pleb.index.get(email=self.email)

    def test_create_auto_tag_relationship_success(self):
        tag_list = []
        for item in range(0,9):
            tag = SBAutoTag(tag_name='test_tag'+str(uuid1()))
            tag.save()
            tag_list.append(tag)
        res = create_tag_relations(tag_list)

        self.assertTrue(res)

    def test_create_auto_tag_relationship_empty_list(self):
        res = create_tag_relations([])

        self.assertFalse(res)

    def test_create_auto_tag_relationship_tag_does_not_exist(self):
        tag_list = ['test', 'sending', 'string', 'instead', 'of', 'object']
        res = create_tag_relations(tag_list)

        self.assertFalse(res)
