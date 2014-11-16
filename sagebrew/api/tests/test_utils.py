from django.test import TestCase

from api.utils import (language_filter, add_failure_to_queue)



class TestLanguageFilterUtil(TestCase):
    def setUp(self):
        self.vulgar_words = 'anal anus ballsack blowjob blow job boner'

    def test_language_filter(self):
        res = language_filter(self.vulgar_words)

        self.assertNotEqual(res, self.vulgar_words)

    def test_language_filter_not_profane(self):
        sentence = "The quick brown fox jumped over the lazy dog."

        res = language_filter(sentence)

        self.assertEqual(res, sentence)


class TestAddFailureToQueue(TestCase):
    def setUp(self):
        self.message = {
            'message': 'this is a test message to add if a task fails'
        }

    def test_adding_failure_to_queue(self):
        self.assertTrue(add_failure_to_queue(self.message))


