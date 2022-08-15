import csv
import requests
import json
from fake_useragent import UserAgent
from requests import HTTPError

MAIN_URL = 'https://api.hh.ru/'
HEADERS = {'User-Agent': UserAgent().chrome}


def get_json(url, params = None):
    """Запрос json файла с вакансиями"""
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        return response.json()['items']
    except HTTPError as http_err:
        print(f'[INFO]: HTTP error: {http_err}')


def get_content(vacancy_name, num_page=1):
    """Получение списка словарей со всеми вакансиями"""

    params = {'text': vacancy_name, 'per_page': 100}
    content = []

    for page_index in range(num_page):
        params['page'] = page_index
        next_page_content = get_json(MAIN_URL+'vacancies/', params)

        if next_page_content:
            content += next_page_content
            print(f'[INFO]: Обработанно {page_index+1} из {num_page} страниц')

    return content


def main():
    print(len(get_content('Переводчик', 3)))


if __name__ == '__main__':
    main()
