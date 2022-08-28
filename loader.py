from fake_useragent import UserAgent
from requests import HTTPError
import requests


class Loader(object):

    key_word = ''
    area_id = None
    data = list()
    MAIN_URL = 'https://api.hh.ru/vacancies/'
    HEADERS = {'User-Agent': UserAgent().chrome}

    def __init__(self, key_word: str) -> None:
        self.key_word = key_word

    def load(self, count_page: int, info: bool) -> None:
        """Производит загрузку данных"""
        data = []
        for page_index in range(count_page):
            try:
                data_raw = self._get_page(page_index)
                data_unpack = self._get_unpacked_page(data_raw)
                data += data_unpack
                if not data_unpack:
                    break
                if info:
                    print(f'[INFO]: Обработанно {page_index+1} из {count_page} страниц')
            except HTTPError as http_err:
                print(f'[INFO]: HTTP error: {http_err}')
        if info:
            print(f'\nБыло собрано {len(data)} вакансий\n')
        self.data = data

    def get_data(self) -> list:
        """Возвращвет загруженные данные"""
        return self.data

    def _get_json(self, url: str, params: dict) -> dict:
        """Возвращает словарь из http запроса"""
        responce = requests.get(
            self.MAIN_URL+url, headers=self.HEADERS, params=params)
        return responce.json()

    def _get_page(self, page_index: int) -> list:
        """Возвращает словарь со страницей вакансий"""
        params = {'text': self.key_word, 'per_page': 10, 'page': page_index}
        page = self._get_json('', params)
        if 'items' in page:
            return page['items']
        return []

    def _get_unpacked_page(self, data_raw: list) -> list:
        """Возвращает словарь с распакованной страницей вакансий"""
        session = requests.Session()
        unpacked_page = []
        for vacancy_raw in data_raw:
            try:
                vacancy = session.get(self.MAIN_URL+f'{vacancy_raw["id"]}').json()
                unpacked_page.append(vacancy)
            except HTTPError as http_err:
                print(f'[INFO]: HTTP error: {http_err}')
        session.close()
        return unpacked_page

