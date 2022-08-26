from multiprocessing import context
import requests
import datetime
import csv
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
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


def get_content(vacancy_name, num_page=1, area_id=None):
    """Получение списка словарей со всеми вакансиями"""

    params = {'text': vacancy_name, 'per_page': 10}
    if area_id is not None:
        params['area'] = area_id

    content = []

    for page_index in range(num_page):
        params['page'] = page_index
        next_page_content = get_json(MAIN_URL+'vacancies/', params)

        if next_page_content:
            content += content_filter(next_page_content)
            print(f'[INFO]: Обработанно {page_index+1} из {num_page} страниц')

    print(f'\n[INFO]: Всего собрано {len(content)} вакансий\n')

    return content


def save_csv(content, sq_plot, ds_plot, cq_plot, key_word='unknow'):
    """Сохранение результатов в csv файл"""
    time_now = datetime.datetime.now().strftime('%d_%m_%y_%H_%M')

    if not os.path.isdir(f'data/[{key_word}] {time_now}'):
        os.mkdir(f'data/[{key_word}] {time_now}')

    mpl.rcParams['font.size'] = 5.0

    plt.figure(clear=True, figsize=(5, 3), dpi=1000)
    plt.bar(sq_plot[0], sq_plot[1])
    plt.xticks(rotation = 90)
    plt.title('Востребованность навыков')
    plt.tight_layout()
    plt.savefig(f'data/[{key_word}] {time_now}/skills_quantity.png')

    plt.figure(clear=True, figsize=(5, 3), dpi=1000)
    plt.bar(cq_plot[0], cq_plot[1])
    plt.xticks(rotation = 90)
    plt.title('Вакансии в городах')
    plt.tight_layout()
    plt.savefig(f'data/[{key_word}] {time_now}/city_quantity.png')

    plt.figure(clear=True, figsize=(5, 3), dpi=1000)
    plt.bar(ds_plot[0], ds_plot[1])
    plt.xticks(rotation = 90)
    plt.title('Зависимость количества вакансий от зарплат')
    plt.tight_layout()
    plt.savefig(f'data/[{key_word}] {time_now}/distribution_salaries.png')

    fieldnames = [
        'name', 'city', 'address',
        'key_skills', 'sal_from', 'sal_to',
        'currency', 'company', 'experience',
        'schedule','published_at', 'description', 
        'alternate_url', 'id'
    ]
    with open(f'data/[{key_word}] {time_now}/vacancies.csv', 'w', newline='', encoding='utf8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for row in content:
            writer.writerow(row)


def get_dependence_skills_quantity(content):
    """Возврощает распределение ключевых навыков по частоте упоминантя в вкансиях"""
    key_skills = []
    for items in list(map(lambda x: x['key_skills'], content)):
        key_skills += list(map(lambda x: x.lower(),items))
    
    key_skills_set = list(set(key_skills))

    total_vacancies = sum([key_skills.count(i) for i in key_skills_set])

    dependence = {}
    for i in key_skills_set:
        count = key_skills.count(i)
        if count/total_vacancies*100 > 0.5:
            skill = i
            if len(i) > 23:
                skill = i[:23] + '...'
            dependence.update({skill: count})

    items = dependence.items()
    items = sorted(list(map(lambda x: [x[1], x[0]], items)))
    groups = list(map(lambda x: x[1], items))
    counts = list(map(lambda x: x[0]/total_vacancies*100, items))

    return [groups, counts]


def get_distribution_salaries(content, min_border=10000, max_border=250000):
    """Возврощает зависимость зарплаты от количества вакансий"""
    
    def get_salary_or_None(salary, cur):
        if cur == 'RUR':
            if type(salary) is int:
                return salary

    salary = []
    for vacancy in content:

        salary_from = get_salary_or_None(vacancy['sal_from'], vacancy['currency'])
        salary_to = get_salary_or_None(vacancy['sal_to'], vacancy['currency'])

        if salary_from:
            salary.append(salary_from)

        if salary_to:
            salary.append(salary_to)

    
    salary.sort()
    salary_min = min_border
    salary_max = max_border
    step = 10000

    dependence = []
    groups = []

    for i in range(salary_min, salary_max, step):
        dependence_step = 0
        groups.append(f'{round(i/1000)}-{round((i+step)/1000)}')
        for j in salary:
            if i < j <= i + step:
                dependence_step += 1
        dependence.append(dependence_step)

    vacancy_len = len(salary)
    for i in range(len(dependence)):
        dependence[i] = dependence[i]*100/vacancy_len

    return [groups, dependence]


def get_dependence_city_quantity(content):
    """Возврощает зависимость городов от количества вкакнсий"""
    cities = []
    for item in list(map(lambda x: x['city'], content)):
        if item:
            cities.append(item)
    
    cities_set = list(set(cities))

    total_vacancies = len(content)

    dependence = {}
    for i in cities_set:
        count = cities.count(i)
        if count/total_vacancies*100 > 0.5:
            dependence.update({i: count})

    items = dependence.items()
    items = sorted(list(map(lambda x: [x[1], x[0]], items)))
    groups = list(map(lambda x: x[1], items))
    counts = list(map(lambda x: x[0], items))

    return [groups, counts]


def text_interface():
    print("Введите название вакансии:\n")

    name = input(">>> ")
    print('\n')

    print("Сколько собрать страниц?\n")

    count_page = int(input(">>> "))
    print("\n")

    content = get_content(name, count_page, area_id=None)
    sq_plot = get_dependence_skills_quantity(content)
    cq_plot = get_dependence_city_quantity(content)
    ds_plot = get_distribution_salaries(content, 10000, 400000)

    save_csv(content, sq_plot, ds_plot, cq_plot, key_word=name)
    print("\nДанне успешно сохранены\n")


def main():
    text_interface()


if __name__ == '__main__':
    main()

