from django.contrib.auth.models import User
from django.test import TestCase

from words.models import Word
from words.serializer import serialize_learning_state


class SerializerTest(TestCase):
    def test_converts_learning_state_to_dict(self):
        test_word = Word.objects.create(
            value='test_word',
            spelling='spelling',
            raw_od_article='raw_od_article'
        )
        test_word.pronunciation_set.create(
            audio='test_mp3'
        )
        test_word.meaning_set.create(
            value='test_value'
        )
        user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password='123456'
        )
        ls = test_word.wordlearningstate_set.create(user=user)
        test_word_dict = serialize_learning_state(ls)
        self.assertEqual(test_word_dict['value'], 'test_word')
        self.assertEqual(test_word_dict['audio'][0]['src'], '/media/test_mp3')
        self.assertEqual(test_word_dict['audio'][0]['id'], 'audio_1')
        self.assertEqual(test_word_dict['meanings'][0]['value'], 'test_value')
        self.assertEqual(test_word_dict['meanings'][0]['id'], 'meaning_1')
        self.assertEqual(len(test_word_dict['audio']), 1)
        self.assertEqual(len(test_word_dict['meanings']), 1)

    def test_assigns_best_audio_from_preferred_pronunciation_field(self):
        test_word = Word.objects.create(
            value='test_word',
            spelling='spelling',
            raw_od_article='raw_od_article'
        )
        test_word.pronunciation_set.create(
            audio='test_1_mp3'
        )
        best_pronunc = test_word.pronunciation_set.create(
            audio='test_2_mp3'
        )
        test_word.meaning_set.create(
            value='test_value'
        )
        user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password='123456'
        )
        ls = test_word.wordlearningstate_set.create(
            user=user,
            preferred_pronunciation=best_pronunc
        )
        test_word_dict = serialize_learning_state(ls)
        self.assertEqual(test_word_dict['audio'][1]['best'], True)

    def test_assigns_first_audio_as_best_for_new_learning_state(self):
        test_word = Word.objects.create(
            value='test_word',
            spelling='spelling',
            raw_od_article='raw_od_article'
        )
        test_word.pronunciation_set.create(
            audio='test_1_mp3'
        )
        test_word.pronunciation_set.create(
            audio='test_2_mp3'
        )
        test_word.meaning_set.create(
            value='test_value'
        )
        user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password='123456'
        )
        ls = test_word.wordlearningstate_set.create(
            user=user
        )
        test_word_dict = serialize_learning_state(ls)
        self.assertEqual(test_word_dict['audio'][0]['best'], True)
