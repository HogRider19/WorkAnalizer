from multiprocessing import context
import requests
import datetime
import csv 
import json
import os
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


def content_filter(content_page):
    """Отбирает определенные поля из словаря с вакансиями"""
    required_fields = ['id', 'name', 'area', 'salary', 'address', 'published_at', 'url', 'employer', 'snippet']

    filter_content_page = []
    for content in content_page:
        filter_content = {}
        for required_field in required_fields:
            filter_content[required_field] = content[required_field]

        filter_content_page.append(filter_content)
    
    return filter_content_page


def get_content(vacancy_name, num_page=1):
    """Получение списка словарей со всеми вакансиями"""

    params = {'text': vacancy_name, 'per_page': 100}
    content = []

    for page_index in range(num_page):
        params['page'] = page_index
        next_page_content = get_json(MAIN_URL+'vacancies/', params)

        if next_page_content:
            content += content_filter(next_page_content)
            print(f'[INFO]: Обработанно {page_index+1} из {num_page} страниц')

    print(f'\n[INFO]: Всего собрано {len(content)} вакансий\n')

    return content


def save_csv(content, key_word='unknow'):
    """Сохранение результатов в csv файл"""
    time_now = datetime.datetime.now().strftime('%d_%m_%y_%H_%M')

    with open(f'data/[{key_word}] {time_now}.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=content[0].keys())

        writer.writeheader()
        for row in content:
            writer.writerow(row)




def main():
    content = get_content('Python develper', 1)
    save_csv(content, 'Python develper')


if __name__ == '__main__':
    main()
