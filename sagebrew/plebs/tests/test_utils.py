from uuid import uuid1

import pickle
from django.test import TestCase
from django.contrib.auth.models import User
from neomodel.exception import DoesNotExist

from plebs.neo_models import Pleb, FriendRequest
from plebs.utils import create_friend_request_util
from plebs.serializers import generate_username
from sb_registration.utils import create_user_util_test


# TODO add this back in
'''
    Until we have a stable version of Neo4J in circle and everywhere else
    on our machines and aren't working with SaaS for some instances of Neo
    I'm commenting this out. We've proved out the functionality with the current
    iterations of py2neo 1.6.x, neomodel 1.x, and neo4j 2.1.x.
    def test_connection_refused(self):
        check_call("sudo service neo4j-service stop", shell=True)
        res = prepare_user_search_html(self.user.username)
        if environ.get("CIRCLECI", "false") == "true":
            check_call("sudo nohup service neo4j-service start > "
                       "%s/neo4j_logs.log &" % environ.get("CIRCLE_ARTIFACTS",
                                                           "/home/logs"),
                       shell=True)
            self.assertIsNone(res)
'''


class TestPleb(TestCase):

    def test_pickle_does_not_exist(self):
        try:
            Pleb.nodes.get(email="notanemail@example.com")
        except(Pleb.DoesNotExist, DoesNotExist) as e:
            pickle_instance = pickle.dumps(e)
            self.assertTrue(pickle_instance)
            self.assertTrue(pickle.loads(pickle_instance))


class TestCreateFriendRequestUtil(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.pleb1 = create_user_util_test(self.email)
        self.user1 = User.objects.get(email=self.email)
        self.email2 = "bounce@simulator.amazonses.com"
        self.pleb2 = create_user_util_test(self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_create_friend_request_util_success(self):
        res = create_friend_request_util(self.pleb1.username,
                                         self.pleb2.username,
                                         str(uuid1()))

        self.assertTrue(res)

    def test_create_friend_request_util_success_already_sent(self):
        friend_request = FriendRequest(object_uuid=str(uuid1()))
        friend_request.save()
        self.pleb1.friend_requests_sent.connect(friend_request)
        self.pleb2.friend_requests_received.connect(friend_request)
        friend_request.request_to.connect(self.pleb2)
        friend_request.request_from.connect(self.pleb1)

        res = create_friend_request_util(self.pleb1.username,
                                         self.pleb2.username,
                                         str(uuid1()))

        self.assertTrue(res)

    def test_create_friend_request_util_fail_pleb_does_not_exist(self):
        res = create_friend_request_util(from_username=self.pleb1.username,
                                         to_username=str(uuid1()),
                                         object_uuid=str(uuid1()))

        self.assertIsInstance(res, DoesNotExist)

    def test_create_friend_request_util_fail_pleb_does_not_exist_pickle(self):
        res = create_friend_request_util(from_username=self.pleb1.username,
                                         to_username=str(uuid1()),
                                         object_uuid=str(uuid1()))
        pickle_instance = pickle.dumps(res)
        self.assertTrue(pickle_instance)
        self.assertTrue(pickle.loads(pickle_instance))


class TestGenerateUsername(TestCase):

    def test_generate_username(self):
        res = generate_username("Test", "Username")
        self.assertEqual(res, "test_username")

    def test_long_username(self):
        res = generate_username("Thisisasuperlong",
                                "fistandlastnamecombination")
        self.assertEqual(res, "thisisasuperlong_fistandlastna")
