import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from sb_posts.neo_models import SBPost
from sb_posts.tasks import (delete_post_and_comments, save_post_task,
                            edit_post_info_task,
                            create_downvote_post, create_upvote_post,
                            flag_post_task)
from plebs.neo_models import Pleb


class TestSavePostTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.index.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_save_post_task(self):
        response = save_post_task.apply_async(kwargs=self.post_info_dict)

        self.assertTrue(response.get())

class TestDeletePostTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.index.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_delete_post_task(self):
        save_response = save_post_task.apply_async(kwargs=self.post_info_dict)
        time.sleep(1)
        delete_response = delete_post_and_comments.apply_async(
            [self.post_info_dict['post_uuid'], ])

        self.assertTrue(save_response.get())
        self.assertTrue(delete_response.get())

class TestEditPostTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.index.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_edit_post_task(self):
        post = SBPost(post_id=uuid1(), content="test post")
        post.last_edited_on = datetime.now(pytz.utc)
        post.save()
        edit_post_dict = {'content': 'Post edited',
                          'post_uuid': post.post_id,
                          'current_pleb': self.pleb.email}
        edit_response = edit_post_info_task.apply_async(kwargs=edit_post_dict)
        edit_response = edit_response.get()
        self.assertTrue(edit_response)



class TestPostTaskRaceConditions(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.index.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_race_condition_edit_delete_post_tasks(self):
        edit_post_dict = {'content': 'Post edited',
                          'post_uuid': self.post_info_dict['post_uuid'],
                          'current_pleb': self.pleb.email,
                          'last_edited_on': datetime.now(pytz.utc)}
        save_response = save_post_task.apply_async(kwargs=self.post_info_dict)
        time.sleep(1)
        edit_response = edit_post_info_task.apply_async(kwargs=edit_post_dict)
        time.sleep(1)
        delete_response = delete_post_and_comments.apply_async(
            [self.post_info_dict['post_uuid'], ])

        self.assertTrue(save_response.get())
        self.assertTrue(edit_response)
        self.assertTrue(delete_response.get())

    def test_race_condition_edit_multiple_times(self):
        edit_array = []
        save_response = save_post_task.apply_async(kwargs=self.post_info_dict)

        edit_dict = {'content': "post edited",
                     'post_uuid': self.post_info_dict['post_uuid'],
                     'current_pleb': self.pleb.email,
                     'last_edited_on': datetime.now(pytz.utc)}
        for num in range(1, 10):
            edit_dict['content'] = "post edited" + str(num)
            edit_dict['last_edited_on'] = datetime.now(pytz.utc)
            edit_response = edit_post_info_task.apply_async(kwargs=edit_dict)
            edit_array.append(edit_response)

        self.assertTrue(save_response.get())
        for response in edit_array:
            self.assertTrue(response)


class TestMultipleTasks(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.index.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_create_many_posts(self):
        response_array = []
        for num in range(1, 10):
            uuid = str(uuid1())
            self.post_info_dict['post_uuid'] = uuid
            save_response = save_post_task.apply_async(kwargs=self.post_info_dict)
            response_array.append(save_response.get())

        for item in response_array:
            self.assertTrue(item)

    def test_create_many_votes(self):
        vote_array = []
        vote_info_dict = {"post_uuid": self.post_info_dict['post_uuid'],
                          "pleb": self.pleb.email}
        response = save_post_task.apply_async(kwargs=self.post_info_dict)
        response = response.get()

        for num in range(1, 10):
            uvote_response = create_upvote_post.apply_async(
                kwargs=vote_info_dict)
            dvote_response = create_downvote_post.apply_async(
                kwargs=vote_info_dict)
            vote_array.append(uvote_response.get())
            vote_array.append(dvote_response.get())
        self.assertTrue(response)
        for item in vote_array:
            self.assertTrue(item)

    def test_create_same_post_twice(self):
        post_info_dict = {'current_pleb': self.pleb.email,
                          'wall_pleb': self.pleb.email,
                          'content': 'test post',
                          'post_uuid': str(uuid1())}
        response1 = save_post_task.apply_async(kwargs=post_info_dict)
        response1 = response1.get()
        time.sleep(1)
        response2 = save_post_task.apply_async(kwargs=post_info_dict)

        self.assertTrue(response1)
        self.assertFalse(response2.get())

class TestFlagPostTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.index.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_flag_post_task_success_spam(self):
        post = SBPost(post_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.post_id, 'current_user': self.pleb.email,
                     'flag_reason': 'spam'}

        res = flag_post_task.apply_async(kwargs=task_dict)

        self.assertTrue(res.get())

    def test_flag_post_task_success_explicit(self):
        post = SBPost(post_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.post_id, 'current_user': self.pleb.email,
                     'flag_reason': 'explicit'}

        res = flag_post_task.apply_async(kwargs=task_dict)

        self.assertTrue(res.get())

    def test_flag_post_task_success_other(self):
        post = SBPost(post_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.post_id, 'current_user': self.pleb.email,
                     'flag_reason': 'other'}

        res = flag_post_task.apply_async(kwargs=task_dict)

        self.assertTrue(res.get())

    def test_flag_post_task_failure_incorrect_reason(self):
        post = SBPost(post_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.post_id, 'current_user': self.pleb.email,
                     'flag_reason': 'dumb'}

        res = flag_post_task.apply_async(kwargs=task_dict)

        self.assertFalse(res.get())

    def test_flag_post_task_post_does_not_exist(self):
        task_dict = {'post_uuid': uuid1(), 'current_user': self.pleb.email,
                     'flag_reason': 'other'}

        res = flag_post_task.apply_async(kwargs=task_dict)

        self.assertFalse(res.get())

    def test_flag_post_task_user_does_not_exist(self):
        post = SBPost(post_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.post_id, 'current_user': uuid1(),
                     'flag_reason': 'other'}

        res = flag_post_task.apply_async(kwargs=task_dict)

        self.assertFalse(res.get())