from fake_useragent import UserAgent
from requests import HTTPError
import requests
from . import config
import aiohttp
import asyncio
import time
import random
from progress.bar import ChargingBar


class Loader:

    _MAIN_URL = config.MAIN_URL

    def __init__(self, key_word: str) -> None:
        self._key_word = key_word
        self.headers = {}
        self._data = []

    def load(self, count_page: int, params: dict, info: bool = True):
        """Начинает загрузку данных"""
        ids = self._get_vacancies_id(count_page*10, params)

        self._bar = ChargingBar('Processing', max=len(ids))
        data = asyncio.run(self._load_data_using_id(ids))
        self._bar.finish()

        self._data = data 

    def get_data(self):
        return self._data

    def update_useragent(self):
        self.headers.update({'User-Agent': UserAgent().chrome})

    def _get_vacancies_id(self, count: int, params: dict):
        session = requests.Session()
        base_params = {'text': self._key_word, 'per_page': 100, 'page': 0}
        base_params.update(params)

        ids = []
        for page_index in range(round(count/100) + 1):
            base_params.update({'page': page_index})
            try:
                page = session.get(
                    self._MAIN_URL,
                    params=base_params,
                    headers=self.headers).json()

                if 'items' in page:
                    ids.extend(map(lambda v: v['id'], page['items']))
                else:
                    break
            except HTTPError as http_error:
                print(f'[INFO]: HTTP error: {http_error}')

        return ids

    async def _load_data_using_id(self, ids: list):
        data = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for id in ids:
                tasks.append(asyncio.create_task(self._load_vacancy_info(id, session)))

            for index, task in enumerate(tasks):
                if index % 20 == 0:
                    self.update_useragent()
                    time.sleep(1) 
                data.append(await task)
        return data

    async def _load_vacancy_info(self, id: list, session):
        async with session.get(f"{self._MAIN_URL}{id}") as response:
            json = await response.json()
            self._bar.next()
            return json


'''
class Loader(object):

    key_word = ''
    area_id = None
    data = list()
    MAIN_URL = 'https://api.hh.ru/vacancies/'
    HEADERS = {'User-Agent': UserAgent().chrome}

    def __init__(self, key_word: str) -> None:
        self.key_word = key_word

    def load(self, count_page: int, params: dict = {}, info: bool = True) -> None:
        """Производит загрузку данных"""
        data = []
        for page_index in range(count_page):
            try:
                data_raw = self._get_page(page_index, params)
                data_unpack = self._get_unpacked_page(data_raw)
                data += data_unpack
                if not data_unpack:
                    break
                if info:
                    print(
                        f'[INFO]: Обработанно {page_index+1} из {count_page} страниц')
            except HTTPError as http_err:
                print(f'[INFO]: HTTP error: {http_err}')
        if info:
            print(f'\nБыло собрано {len(data)} вакансий\n')
        self.data = data

    def get_data(self) -> list:
        """Возвращвет загруженные данные"""
        return self.data

    def update_useragent(self):
        """Изменяет useragent у класса"""
        self.HEADERS.update({'User-Agent': UserAgent().chrome})

    def _get_json(self, url: str, params: dict) -> dict:
        """Возвращает словарь из http запроса"""
        responce = requests.get(
            self.MAIN_URL+url, headers=self.HEADERS, params=params)
        return responce.json()

    def _get_page(self, page_index: int, add_params: dict) -> list:
        """Возвращает словарь со страницей вакансий"""
        params = {'text': self.key_word, 'per_page': 10, 'page': page_index}
        params.update(add_params)
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
                vacancy = session.get(
                    self.MAIN_URL+f'{vacancy_raw["id"]}').json()
                unpacked_page.append(vacancy)
            except HTTPError as http_err:
                print(f'[INFO]: HTTP error: {http_err}')
        session.close()
        return unpacked_page
'''