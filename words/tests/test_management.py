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


class ODImporterTest(TestCase):
    @fudge.patch('words.management.commands._od_importer.requests.get')
    @override_settings(OXFORD_DICTIONARY_APP_ID='test_app_id',
                       OXFORD_DICTIONARY_APP_KEY='test_app_key')
    def test_uses_requests_to_get_article_from_od(self, fake_get):
        url = 'https://od-api.oxforddictionaries.com'
        expected_headers = {'app_id': 'test_app_id', 'app_key': 'test_app_key'}
        fake_get.expects_call().with_args(arg.contains(
            url), headers=expected_headers).returns(FakeRequestsResponse('{}'))
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
        fake_get.expects_call().raises(requests.exceptions.HTTPError(http_error))
        test_word = ODImporter('third')
        msg, res = test_word.get_article('', '')
        self.assertEqual(msg, 'Specified word does not exist in Oxford Dictionary')

    @fudge.patch('words.management.commands._od_importer.requests.get')
    def test_uses_requests_to_raise_not_404_http_error(self, fake_get):
        http_error = 418
        fake_get.expects_call().raises(requests.exceptions.HTTPError(http_error))
        test_word = ODImporter('fourth')
        msg, res = test_word.get_article('', '')
        self.assertEqual(msg, 'HTTP error {} occurred'.format(
            requests.exceptions.HTTPError(http_error)))

    @fudge.patch('words.management.commands._od_importer.requests.get')
    @fudge.patch('words.management.commands._od_importer.ODImporter.make_abs_path')
    @fudge.patch('words.management.commands._od_importer.ODImporter.save_article')
    def test_positive_case(self, fake_get, fake_abs_path, fake_save_article):
        url = 'https://od-api.oxforddictionaries.com'
        expected_headers = {'app_id': 'another_test_app_id',
                            'app_key': 'another_test_app_key'}
        dir_path = os.path.join(settings.BASE_DIR, 'media',
                                'od')
        fake_get.expects_call().with_args(arg.contains(
            url), headers=expected_headers).returns(
            FakeRequestsResponse('{"article": "article"}'))
        fake_abs_path.expects_call().returns('')
        fake_save_article.expects_call().returns(None)
        test_word = ODImporter('fifth')
        msg = test_word.create_word_article(dir_path, 'another_test_app_id',
                                            'another_test_app_key')
        self.assertEqual(msg, 'Data successfully saved')

    # @fudge.patch('builtins.open')
    # def test_save_files_to_proper_dir(self, fake_open):
    #     fake_file = fudge.Fake().is_a_stub()
    #     fake_file.provides("write").is_callable()
    #     fake_open.expects_call().is_a_stub().returns(fake_file)
    #     test_word = ODImporter('fifth')
    #     msg = test_word.save_article('', '')
    #     self.assertEqual(msg, '1')
    # Убедиться что функция 'create_word_article' сохраняет файлы в нужную директорию

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
            "word": "first"
        }
        fake_post.expects_call().with_args(arg.contains(url), data=expected_data).returns(
            FakeRequestsResponse('some html code'))
        test_word = ForvoImporter('first')
        res = test_word.get_html_from_forvo()
        self.assertEqual(res, 'some html code')
        # проверить что метод 'get_html_from_forvo' получает корректные данные
        # при отправке корректного запроса

    @fudge.patch('words.management.commands._forvo_importer.requests.post')
    def test_uses_requests_to_raise_connection_error(self, fake_post):
        fake_post.expects_call().raises(requests.exceptions.ConnectionError)
        test_word = ForvoImporter('second')
        res = test_word.get_html_from_forvo()
        self.assertEqual(res, 'Connection error')
        # что будет, если произойдет ConnectionError

    def test_3(self):
        # что будет, если вернется http ошибка
        pass

    def test_5(self):
        # что будет, если нет прав на запись в директорию
        pass

    def test_if_forvo_reply_does_not_contain_class_intro(self): # html не соответствует тому что мы ожидали
        html = '<html><div class="no_intro">some data</div></html>'
        test_word = ForvoImporter('something')
        res = test_word.get_raw_json_from_html(html)
        self.assertEqual(res, '1111111111')
        # что будет, если структура ответа от forvo изменилась
        # и в html отсутствует тэг с классом "intro"
        pass

    def test_7(self): # один тест для проверки html
        # что будет, если структура ответа от forvo изменилась
        # и тэг с классом "intro" теперь находися после тэга "pre"
        pass

    def test_8(self):
        # что будет, если структура ответа от forvo изменилась
        # и в html отсутствует тэг pre
        pass

    def test_9(self):
        # что будет если json не корректный
        # что будет, если в json отсутствует ключ "item"
        pass

    def test_10(self):
        # что будет, если в словаре "item" отсутствует ключ "pathmp3"
        pass

    def test_11(self):
        # проверить что создается директория с именем конкретного слова
        pass

    def test_12(self):
        # что будет, если директория с именем конкретного слова уже существует
        pass

    def test_13(self):
        # проверить, есть ли доступ "запись" в директорию
        # с именем конкретного слова
        pass

    def test_14(self):
        # проверить что имя полного пути для файла создается корректно
        pass

    def test_15(self):
        # проверить что скачивается корректный mp3 файл, если переданы
        # корректные параметры
        pass

    def test_16(self):
        # что если при скачивании mp3 возникнет ошибка
        pass

    def test_17(self):
        # что если при скачивании mp3 возникнет ошибка http - убрать
        pass

    def test_18(self):
        # что будет, если в словаре items у ключей code и
        # country отсутствуют занчения en и United States соответственно
        pass

    def test_19(self):
        # Убедиться что функция 'save_result' сохраняет файлы
        # в нужную директорию
        pass

    def test_positive_case(self):
        # проверить что будет, если все хорошо
        pass
