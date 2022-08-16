from multiprocessing import context
import requests
import datetime
import csv 
import matplotlib.pyplot as plt
import numpy as np
from fake_useragent import UserAgent
from requests import HTTPError

MAIN_URL = 'https://api.hh.ru/'
HEADERS = {'User-Agent': UserAgent().chrome}


def get_json(url, params = None):
    """Запрос json файла с вакансиями"""
    session = requests.Session()
    response = session.get(url, params=params, headers=HEADERS)

    if response.status_code == 200:
        items = list(map(lambda x: x['id'], response.json()['items']))
        content_list = []
        for index, content_id in enumerate(items):
            try:
                content = session.get(url+f'{content_id}', headers=HEADERS).json()
                content_list.append(content)
            except HTTPError as http_err:
                print(f'[INFO]: HTTP error: {http_err}')
        session.close()
        return content_list
    else:
        return []



def content_filter(content_page):
    """Отбирает определенные поля из словаря с вакансиями"""
    required_fields = ['id', 'name', 'published_at', 'alternate_url', 'description', 'key_skills']

    filter_content_page = []
    for content in content_page:
        filter_content = {}
        for required_field in required_fields:
            filter_content[required_field] = content[required_field]

        def none_filter(data_dict, kw):
            try:
                return data_dict[kw]
            except TypeError:
                return '' 

        filter_content['sal_from'] = none_filter(content['salary'], 'from')
        filter_content['sal_to'] = none_filter(content['salary'], 'to')
        filter_content['currency'] = none_filter(content['salary'], 'currency')
        filter_content['city'] = none_filter(content['address'], 'city')
        filter_content['address'] = none_filter(content['address'], 'street')
        filter_content['company'] = none_filter(content['employer'], 'name')
        filter_content['experience'] = none_filter(content['experience'], 'name')
        filter_content['schedule'] = none_filter(content['schedule'], 'name')

        filter_content['key_skills'] = []
        if content['key_skills'] is not None:
            for key_skill in content['key_skills']:
                filter_content['key_skills'].append(key_skill['name'])
        else:
            filter_content['key_skills'] = []

        filter_content_page.append(filter_content)
    
    return filter_content_page


def get_content(vacancy_name, num_page=1, ):
    """Получение списка словарей со всеми вакансиями"""

    params = {'text': vacancy_name, 'per_page': 10}
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

    with open(f'data/[{key_word}] {time_now}.csv', 'w', newline='', encoding='utf8') as file:
        writer = csv.DictWriter(file, fieldnames=content[0].keys())

        writer.writeheader()
        for row in content:
            writer.writerow(row)


def get_dependence_skills_quantity(content):
    key_skills = []
    for items in list(map(lambda x: x['key_skills'], content)):
        key_skills += list(map(lambda x: x.lower(),items))
    
    key_skills_set = list(set(key_skills))

    dependence = {}
    for i in key_skills_set:
        count = key_skills.count(i)
        if count > 20:
            dependence.update({i: count})

    items = dependence.items()
    items = sorted(list(map(lambda x: [x[1], x[0]], items)))
    groups = list(map(lambda x: x[1], items))
    counts = list(map(lambda x: x[0], items))
    plt.bar(groups, counts)
    plt.xticks(rotation = 90)
    plt.show()
    




def main():
    content = get_content('Python develper', 30)
    save_csv(content, key_word='Python develper')
    get_dependence_skills_quantity(content)


if __name__ == '__main__':
    main()

