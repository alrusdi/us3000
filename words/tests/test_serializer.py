import fudge
from django.contrib.auth.models import User
from django.test import TestCase

from words.models import Word
from words.serializer import serialize_learning_state

FAKE_FORVO_DATA = {
    "attributes": {
        "total": 2
    },
    "items": [
        {
            "addtime": "2008-04-04 10:19:01",
            "code": "en",
            "country": "United States",
            "hits": 35954,
            "id": 2625,
            "langname": "English",
            "num_positive_votes": 16,
            "num_votes": 17,
            "original": "about",
            "pathmp3": "https://apifree.forvo.com/audio/2c2g25392d2l1j22212a3m2e1f333h32371i3d2i272g1p2f2n3m291g3g2c231b2k2h3e363l3f3q2j1h311n2b1o1f2e2k2p2m3n21251i313q2c1m32372e29243o_1p1p2g3j2q3b1m3k1p1p2a1g1j3q231m3o363q3m2g211t1t",
            "pathogg": "https://apifree.forvo.com/audio/3m3f363l1m2i2e2l322i3a2d3b2a2j2d3b35223l1j3b3j24282o3o36372h1p3k3e2g2b3a3f3f3f3b3c2327311g1h1i3f3c3g313b23251m2g362n212p2d1g341p_3k2n2o1h352728211k1k3o1g3f2o2f2m1b1j343833211t1t",
            "rate": 15,
            "sex": "m",
            "username": "jrbswim1",
            "word": "about"
        },
        {
            "addtime": "2009-02-11 23:47:25",
            "code": "en",
            "country": "United States",
            "hits": 15292,
            "id": 126197,
            "langname": "English",
            "num_positive_votes": 1,
            "num_votes": 2,
            "original": "about",
            "pathmp3": "https://apifree.forvo.com/audio/363h31251k313i1f353d22333q3k1b3p241f1b2f1h393i3l2j271k2i1h211j281n3l3j363i331o213m293m1n2k3d1n3p272j332j22223q1b1p2j3b1o221g3a1o3f3c3d27343g3a2b3i29323b1h1o3a3m3d2o3m1n2k211t1t_3636261j3b3j3m23232i33272l1h233n1m3q382k2n211t1t",
            "pathogg": "https://apifree.forvo.com/audio/2p1i3n1f2a3c283l3q3k3b3g2n2k2m1j3g2a2p3o1m2c2e312o2k3d2c343d3p2c3h2o253n1o293i2e2537353q392l32232k272p3f3j1i3n1j3e212j2d352p372i353q1b222m2j1m2k2n3f22381h213o1p1k2m3p2i362h1t1t_2k3m261o1p2m3p3b21311i23333m2o2q2i361k2l3g211t1t",
            "rate": 0,
            "sex": "m",
            "username": "carsonpowers",
            "word": "about"
        }
    ]
}


class SerializerTest(TestCase):
    @fudge.patch(
        'words.models.WordLearningState._get_pronunciations_meta',
        'words.models.WordLearningState._get_sounds'
    )
    def test_converts_learning_state_to_dict(self, fake_meta, fake_sounds):
        fake_meta.expects_call().returns(FAKE_FORVO_DATA)
        fake_sounds.expects_call().returns(['sound1.mp3', 'sound2.mp3'])

        test_word = Word.objects.create(
            value='test_word',
            spelling='spelling',
            raw_od_article='raw_od_article'
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
        self.assertEqual(test_word_dict['audio'][0]['src'], 'sound1.mp3')
        self.assertEqual(test_word_dict['audio'][0]['id'], 'audio_2625')
        self.assertEqual(test_word_dict['meanings'][0]['value'], 'test_value')
        self.assertEqual(test_word_dict['meanings'][0]['id'], 'meaning_1')
        self.assertEqual(len(test_word_dict['audio']), 2)
        self.assertEqual(len(test_word_dict['meanings']), 1)

    @fudge.patch(
        'words.models.WordLearningState._get_pronunciations_meta',
        'words.models.WordLearningState._get_sounds'
    )
    def test_assigns_best_audio_from_preferred_pronunciation_field(self, fake_meta, fake_sounds):
        fake_meta.expects_call().returns(FAKE_FORVO_DATA)
        fake_sounds.expects_call().returns(['sound1.mp3', 'sound2.mp3'])
        test_word = Word.objects.create(
            value='test_word',
            spelling='spelling',
            raw_od_article='raw_od_article'
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
            preferred_pronunciation=FAKE_FORVO_DATA['items'][1]['id']
        )
        test_word_dict = serialize_learning_state(ls)
        self.assertEqual(test_word_dict['audio'][1]['best'], True)

    @fudge.patch(
        'words.models.WordLearningState._get_pronunciations_meta',
        'words.models.WordLearningState._get_sounds'
    )
    def test_assigns_first_audio_as_best_for_new_learning_state(self, fake_meta, fake_sounds):
        fake_meta.expects_call().returns(FAKE_FORVO_DATA)
        fake_sounds.expects_call().returns(['sound1.mp3', 'sound2.mp3'])
        test_word = Word.objects.create(
            value='test_word',
            spelling='spelling',
            raw_od_article='raw_od_article'
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
