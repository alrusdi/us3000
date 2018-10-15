import logging

from django.conf import settings
from django.test import TestCase, override_settings
from fudge.inspector import arg
from words.management.commands._forvo_importer import ForvoImporter
from words.management.commands._od_importer import ODImporter
import fudge
import requests
import os


class FakeRequestsResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        pass

    def content(self):
        return self.text


class ODImporterTest(TestCase):
    @fudge.patch('words.management.commands._od_importer.requests.get')
    @fudge.patch('builtins.open')
    def test_positive_case(self, fake_get, fake_open):

        class FakeFile:
            def write(self, *args, **kwargs):
                pass

        class FakeContextManager:
            def __enter__(self):
                return FakeFile()

            def __exit__(self, *args):
                pass

        url = 'https://od-api.oxforddictionaries.com'
        expected_headers = {'app_id': 'test_app_id',
                            'app_key': 'test_app_key'}
        dir_path = os.path.join(settings.BASE_DIR, 'media', 'od')
        fake_get.expects_call().with_args(arg.contains(
            url), headers=expected_headers).returns(
            FakeRequestsResponse('{"article": "article"}'))
        fake_open.expects_call().returns(FakeContextManager())
        test_word = ODImporter('fifth')
        msg = test_word.create_word_article(dir_path, 'test_app_id',
                                            'test_app_key')
        self.assertEqual(msg, 'Data successfully saved')

    @fudge.patch('words.management.commands._od_importer.requests.get')
    @override_settings(OXFORD_DICTIONARY_APP_ID='test_app_id',
                       OXFORD_DICTIONARY_APP_KEY='test_app_key')
    def test_uses_requests_to_get_article_from_od(self, fake_get):
        url = 'https://od-api.oxforddictionaries.com'
        expected_headers = {'app_id': 'test_app_id',
                            'app_key': 'test_app_key'}
        fake_get.expects_call().with_args(arg.contains(
            url), headers=expected_headers).returns(
            FakeRequestsResponse('{}'))
        test_word = ODImporter('something')
        msg, res = test_word.get_article(settings.OXFORD_DICTIONARY_APP_ID,
                                         settings.OXFORD_DICTIONARY_APP_KEY)
        self.assertEqual(msg, 'Data successfully saved')

    @fudge.patch('words.management.commands._od_importer.requests.get')
    def test_uses_requests_to_raise_connection_error(self, fake_get):
        fake_get.expects_call().raises(requests.exceptions.ConnectionError)
        test_word = ODImporter('second')
        msg, res = test_word.get_article('', '')
        self.assertEqual(msg, 'Connection error')

    @fudge.patch('words.management.commands._od_importer.requests.get')
    def test_uses_requests_to_raise_404_error(self, fake_get):
        http_error = 404
        fake_get.expects_call().raises(requests.exceptions
                                       .HTTPError(http_error))
        test_word = ODImporter('qwerty')
        msg, res = test_word.get_article('', '')
        self.assertEqual(msg, 'Word "qwerty" does not exist'
                              ' in Oxford Dictionary')

    @fudge.patch('words.management.commands._od_importer.requests.get')
    def test_uses_requests_to_raise_not_404_http_error(self, fake_get):
        http_error = 418
        fake_get.expects_call().raises(requests.exceptions
                                       .HTTPError(http_error))
        test_word = ODImporter('fourth')
        msg, res = test_word.get_article('', '')
        self.assertEqual(msg, 'HTTP error occurred: {}'.format(
            requests.exceptions.HTTPError(http_error)))

    @fudge.patch('builtins.open')
    def test_save_proper_data_to_file(self, fake_open):
        class FakeFile:
            def write(self, *args, **kwargs):
                assert 'some_data' in args

        class FakeContextManager:
            def __enter__(self):
                return FakeFile()

            def __exit__(self, *args):
                pass
        fake_open.expects_call().with_args('some_path', 'w').returns(
            FakeContextManager())
        test_word = ODImporter('fifth')
        test_word.save_article('some_path', 'some_data')

    @fudge.patch('words.management.commands._od_importer.os.path.exists')
    @fudge.patch('words.management.commands._od_importer.os.access')
    def test_write_permissions_of_working_dir(self, fake_path_exists,
                                              fake_dir_access):
        fake_path_exists.expects_call().returns(True)
        fake_dir_access.expects_call().returns(False)
        test_word = ODImporter('sixth')
        msg = test_word.create_word_article('', '', '')
        self.assertEqual(msg, "Permission denied: ''")

    @fudge.patch('words.management.commands._od_importer.os.path.exists')
    def test_is_working_dir_exist(self, fake_path_exists):
        fake_path_exists.expects_call().returns(False)
        test_word = ODImporter('seventh')
        msg = test_word.create_word_article('', '', '')
        self.assertEqual(msg, "Path does not exist: ''")


class ForvoImporterTest(TestCase):
    @fudge.patch('words.management.commands._forvo_importer.requests.post',
                 'words.management.commands._forvo_importer.requests.get',
                 'words.management.commands._forvo_importer.'
                 'ForvoImporter.is_path_exist',
                 'words.management.commands._forvo_importer.'
                 'ForvoImporter.save_mp3')
    def test_positive_case(self, fake_post, fake_get,
                           fake_is_path_exist, fake_save):
        url = 'api.forvo.com'
        expected_data = {
            "action": "word-pronunciations",
            "format": "json",
            "id_lang_speak": "39",
            "id_order": "",
            "limit": "",
            "rate": "",
            "send": "",
            "username": "",
            "word": "fake_word"
        }
        fake_post.expects_call().with_args(
            arg.contains(url), data=expected_data).returns(
            FakeRequestsResponse(
                ('<html><div class="intro"><pre>'
                 ' {&quot;items&quot;: ['
                 '{&quot;code&quot;: &quot;en&quot;, '
                 '&quot;country&quot;: &quot;United States&quot;, '
                 '&quot;pathmp3&quot;: &quot;mp3\/url\/&quot;}'
                 ']}'
                 ' </pre></html>'))
        )
        fake_get.expects_call().returns(FakeRequestsResponse(b'0x11'))
        fake_is_path_exist.expects_call().returns(True)
        fake_save.expects_call().returns(None)
        test_word = ForvoImporter('fake_word')
        res = test_word.import_sound()
        # TODO check if file saved
        self.assertEqual(res, None)

    @fudge.patch('words.management.commands._forvo_importer.requests.post')
    def test_uses_requests_to_get_html_from_forvo(self, fake_post):
        url = 'api.forvo.com'
        expected_data = {
            "action": "word-pronunciations",
            "format": "json",
            "id_lang_speak": "39",
            "id_order": "",
            "limit": "",
            "rate": "",
            "send": "",
            "username": "",
            "word": "fake_word"
        }
        fake_post.expects_call().with_args(
            arg.contains(url), data=expected_data).returns(
            FakeRequestsResponse('some html code')
        )
        test_word = ForvoImporter('fake_word')
        res = test_word.get_html_from_forvo()
        self.assertEqual(res, 'some html code')
        # проверить что метод 'get_html_from_forvo' получает корректные данные
        # при отправке корректного запроса - Ok

    @fudge.patch('words.management.commands._forvo_importer.requests.post')
    def test_uses_requests_to_raise_connection_error_html(self, fake_post):
        fake_post.expects_call().raises(requests.exceptions.ConnectionError)
        test_word = ForvoImporter('fake_word')
        with self.assertLogs(
                logger='general', level='ERROR'
        ) as general, self.assertLogs(
            logger='forvo_fails', level='ERROR'
        ) as forvo:
            test_word.import_sound()
        self.assertEqual([*general.output, *forvo.output],
                         ['ERROR:general:Connection error',
                          'ERROR:forvo_fails:fake_word'])
        # что будет, если произойдет ConnectionError - 1

    @fudge.patch('words.management.commands._forvo_importer.requests.post')
    def test_uses_requests_to_raise_http_error(self, fake_post):
        http_error = 418
        fake_post.expects_call().raises(requests.exceptions.HTTPError(
            http_error))
        test_word = ForvoImporter('fake_word')
        with self.assertLogs(
                logger='general', level='ERROR'
        ) as general, self.assertLogs(
            logger='forvo_fails', level='ERROR'
        ) as forvo:
            test_word.import_sound()
        self.assertEqual([*general.output, *forvo.output],
                         ['ERROR:general:Following http error occurred: 418',
                          'ERROR:forvo_fails:fake_word'])
        # 2

    @fudge.patch('words.management.commands._forvo_importer.requests.post')
    def test_if_forvo_html_response_has_unexpected_structure(self, fake_post):
        url = 'api.forvo.com'
        expected_data = {
            "action": "word-pronunciations",
            "format": "json",
            "id_lang_speak": "39",
            "id_order": "",
            "limit": "",
            "rate": "",
            "send": "",
            "username": "",
            "word": "fake_word"
        }
        fake_post.expects_call().with_args(
            arg.contains(url), data=expected_data).returns(
            FakeRequestsResponse('some unexpected html code')
        )
        test_word = ForvoImporter('fake_word')
        with self.assertLogs(
                logger='general', level='ERROR'
        ) as general, self.assertLogs(
            logger='forvo_fails', level='ERROR'
        ) as forvo:
            test_word.import_sound()
        self.assertEqual([*general.output, *forvo.output],
                         ['ERROR:general:Unexpected HTML Response from Forvo',
                          'ERROR:forvo_fails:fake_word'])
        # html не соответствует тому что мы ожидали - 3

    @fudge.patch('words.management.commands._forvo_importer.requests.post')
    def test_if_json_from_forvo_has_unexpected_structure(self, fake_post):
        url = 'api.forvo.com'
        expected_data = {
            "action": "word-pronunciations",
            "format": "json",
            "id_lang_speak": "39",
            "id_order": "",
            "limit": "",
            "rate": "",
            "send": "",
            "username": "",
            "word": "fake_word"
        }
        html_response = ('<div class="intro"><pre> {&quot;not_items&quot;:'
                         ' [{&quot;pathmp3&quot;: &quot;mp3_url&quot;}]} '
                         '</pre></div>')
        fake_post.expects_call().with_args(
            arg.contains(url), data=expected_data).returns(
            FakeRequestsResponse(html_response)
        )
        test_word = ForvoImporter('fake_word')
        with self.assertLogs(
                logger='general', level='ERROR'
        ) as general, self.assertLogs(
            logger='forvo_fails', level='ERROR'
        ) as forvo:
            test_word.import_sound()
        self.assertEqual([*general.output, *forvo.output],
                         ['ERROR:general:JSON response from Forvo has unexpected structure',
                          'ERROR:forvo_fails:fake_word'])
        # 4

    @fudge.patch('words.management.commands._forvo_importer.requests.post')
    def test_if_json_from_forvo_has_not_required_keys(self, fake_post):
        url = 'api.forvo.com'
        expected_data = {
            "action": "word-pronunciations",
            "format": "json",
            "id_lang_speak": "39",
            "id_order": "",
            "limit": "",
            "rate": "",
            "send": "",
            "username": "",
            "word": "fake_word"
        }
        html_response = ('<div class="intro"><pre> {&quot;items&quot;:'
                         ' [{&quot;pathmp777&quot;: &quot;mp3_url&quot;, '
                         '&quot;code&quot;: &quot;en&quot;,'
                         '&quot;country&quot;: &quot;United States&quot;}]} '
                         '</pre></div>')
        fake_post.expects_call().with_args(
            arg.contains(url), data=expected_data).returns(
            FakeRequestsResponse(html_response)
        )
        test_word = ForvoImporter('fake_word')
        with self.assertLogs(
                logger='general', level='ERROR'
        ) as general, self.assertLogs(
            logger='forvo_fails', level='ERROR'
        ) as forvo:
            test_word.import_sound()
        self.assertEqual([*general.output, *forvo.output],
                         ['ERROR:general:JSON response from Forvo does not have required keys',
                          'ERROR:forvo_fails:fake_word'])
        # что будет если json не корректный - 5

    # @fudge.patch('words.management.commands._forvo_importer.os.mkdir')
    # def test_11(self, fake_create_dir):
    #     fake_create_dir.expects_call().with_args('dir_path')
    #     test_word = ForvoImporter('eleventh')
    #     res = test_word.create_word_dir('dir_path')
        # проверить что создается директория с именем конкретного слова

    @fudge.patch('words.management.commands._forvo_importer.os.mkdir')
    def test_11(self, fake_create_dir):
        fake_create_dir.expects_call().with_args('dir_path')
        test_word = ForvoImporter('eleventh')
        res = test_word.save_result('dir_path')
        # проверить что создается директория с именем конкретного слова

    def test_12(self):
        # что будет, если директория с именем конкретного слова уже существует
        pass

    @fudge.patch('words.management.commands._forvo_importer.ForvoImporter'
                 '.is_path_exist')
    def test_if_dir_path_exists(self, fake_is_path_exist):
        fake_is_path_exist.expects_call().returns(False)
        test_word = ForvoImporter('seventh')
        res = test_word.is_path_exist('not/exist/mp3/path')
        self.assertEqual(res, False)
        # проверить, существует ли путь

    @fudge.patch('words.management.commands._forvo_importer.'
                 'ForvoImporter.is_there_dir_write_permissions')
    def test_write_permission_of_working_dir(self, fake_write_permissions):
        fake_write_permissions.expects_call().returns(False)
        test_word = ForvoImporter('seventh')
        res = test_word.is_there_dir_write_permissions('not/exist/mp3/path')
        self.assertEqual(res, False)
        # проверить, есть ли права записи

    def test_13(self):
        # проверить, есть ли доступ "запись" в директорию
        # с именем конкретного слова
        pass

    def test_if_abs_mp3_path_is_created_correctly(self):
        test_word = ForvoImporter('sixth')
        test_path = test_word.make_mp3_abs_path('audio', 33)
        self.assertEqual(test_path, 'audio/sixth_34.mp3')
        # проверить что имя полного пути для файла создается корректно

    @fudge.patch('words.management.commands._forvo_importer.requests.get')
    def test_uses_requests_to_get_mp3_from_forvo(self, fake_get):
        url = 'correct_mp3_url'
        fake_get.expects_call().returns(FakeRequestsResponse('mp3'))
        test_word = ForvoImporter('tenth')
        res = test_word.get_mp3_from_forvo(url)
        self.assertEqual(res, 'mp3')
        # проверить что скачивается корректный mp3 файл, если переданы
        # корректные параметры

    @fudge.patch('words.management.commands._forvo_importer.requests.get')
    def test_uses_requests_to_raise_connection_error_mp3(self, fake_get):
        url = 'correct/mp3/url'
        fake_get.expects_call().raises(requests.exceptions.ConnectionError)
        test_word = ForvoImporter('eleventh')
        res = test_word.get_mp3_from_forvo(url)
        self.assertEqual(res, None)
        # что если при скачивании mp3 возникнет ошибка

    @fudge.patch('words.management.commands._forvo_importer.'
                 'ForvoImporter.get_html_from_forvo')
    def test_if_forvo_json_does_not_have_required_keys(self, fake_get_html):
        fake_get_html.expects_call().returns(
            ('<html><div class="intro"><pre> {&quot;items&quot;:'
             ' [{&quot;pathmp3&quot;: &quot;mp3/url/&quot;}]} </pre></html>')
        )
        test_word = ForvoImporter('last')
        res = test_word.import_sound()
        self.assertEqual(res, None)
        # что будет, если в словаре items у ключей code и
        # country отсутствуют занчения en и United States соответственно

    @fudge.patch('builtins.open')
    def test_save_proper_data_to_file(self, fake_open):

        class FakeFile:
            def write(self, *args, **kwargs):
                assert 'some_data' in args

        class FakeContextManager:
            def __enter__(self):
                return FakeFile()

            def __exit__(self, *args):
                pass

        fake_open.expects_call().with_args('some_path', 'wb').returns(
            FakeContextManager())
        test_word = ForvoImporter('fifth')
        test_word.save_mp3('some_path', 'some_data')
        # Убедиться что функция 'save_result' сохраняет файлы
        # в нужную директорию
        pass

    # @fudge.patch('builtins.open')
    # def test_save_proper_data_to_file(self, fake_open):
    #     class FakeFile:
    #         def write(self, *args, **kwargs):
    #             assert 'some_data' in args
    #
    #     class FakeContextManager:
    #         def __enter__(self):
    #             return FakeFile()
    #
    #         def __exit__(self, *args):
    #             pass
    #     fake_open.expects_call().with_args('some_path', 'w').returns(
    #         FakeContextManager())
    #     test_word = ODImporter('fifth')
    #     test_word.save_article('some_path', 'some_data')


class ForvoConverterTest(TestCase):
    def test_correctly_format_json(self):
        pass
