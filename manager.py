from storage import Storage
from loader import Loader
from content import Content
import requests
import os


class Manager(object):

    def __init__(self, key_word: str, count_page: int, info: bool = True, params: dict = {}) -> None:
        self.key_word = key_word
        self.count_page = count_page
        self.info = info
        self.params = params
        self.full_description = {
            'city': {'name': 'city_quantity', 'tytle': 'Вакансии в городах'},
            'salary': {'name': 'distribution_salaries', 'tytle': 'Зависимость количества вакансий от зарплат', 'split': False},
            'skill': {'name': 'skills_quantity', 'tytle': 'Востребованность навыков'},
        }   

    def analysis(self, area_id: int = 2) -> None:
        """Производит анализ по заданным параметрам"""
        self._main_analysis()
        
        if self.params.get('city', None):
            self._city_analysis(area_id=area_id)

        if self.params.get('exp', None):
            self._exp_analysis()

        if self.params.get('schedule', None):
            self._schedule_analysis()

    def _main_analysis(self) -> None:
        """Производит анализ полностью по всем вакансиям"""
        loader = Loader(self.key_word)
        loader.load(self.count_page, info=self.info)

        self._loader_processing(loader)


    def _city_analysis(self, area_id: int) -> None:
        """Производит анализ с учетом города"""
        loader = Loader(self.key_word)
        add_params = {'area': area_id}
        loader.load(self.count_page, info=self.info, add_params=add_params)

        responce = requests.get(f'https://api.hh.ru/areas/{area_id}')
        if responce.status_code == 200:
            area_name = responce.json()['name']
        else:
            area_name = area_id

        post_path = self.main_storage.get_main_path() + f'/{area_name}'

        self._loader_processing(loader, post_path=post_path)

    def _exp_analysis(self) -> None: 
        """Производит анализ с учетом опыта работы"""
        add_params = [
            {'experience': 'noExperience'},
            {'experience': 'between1And3'},
            {'experience': 'between3And6'},
            {'experience': 'moreThan6'},
        ]

        if self.info:
            print('\nЗагрузка данных по опыту работы\n')

        exp_dir = f'{self.main_storage.get_main_path()+"/Распределение по опыту"}'
        if not os.path.isdir(exp_dir):
            os.mkdir(f'{exp_dir}')

        group = []
        values = []
        for par in add_params:
            content = self.main_content.get_filter_content(par)
            group.append(par['experience'])
            values.append(len(content.get_data()))
            self._content_processing(content, post_path=exp_dir+f'/{par["experience"]}')

        dep = {'exp': [group, values]}
        info = {'exp': {'name': 'Распределение по опыту', 'tytle': 'Распределение по опыту'}}

        storage = Storage([], dep=dep, post_path=exp_dir)
        storage.save(info)



    def _schedule_analysis(self) -> None:
        """Производит анализ с учетом графика работы"""
        add_params = [
            {'schedule': 'flyInFlyOut'},
            {'schedule': 'remote'},
            {'schedule': 'flexible'},
            {'schedule': 'shift'},
            {'schedule': 'fullDay'},
        ]

        if self.info:
            print('\nЗагрузка данных по графику работы работы\n')

        exp_dir = f'{self.main_storage.get_main_path()+"/Распределение по графику работы"}'
        if not os.path.isdir(exp_dir):
            os.mkdir(f'{exp_dir}')

        group = []
        values = []
        for par in add_params:
            content = self.main_content.get_filter_content(par)
            group.append(par['schedule'])
            values.append(len(content.get_data()))
            self._content_processing(content, post_path=exp_dir+f'/{par["schedule"]}')

        dep = {'schedule': [group, values]}
        info = {'schedule': {'name': 'Распределение по графику работы', 'tytle': 'Распределение по графику работы'}}

        storage = Storage([], dep=dep, post_path=exp_dir)
        storage.save(info)

    def _loader_processing(self, loader: Loader, post_path: str = None, description: dict = None) -> None:
        """Сохранятет данные из загрузчика"""
        data_raw = loader.get_data()
        loader.update_useragent()

        content = Content(data_raw)
        
        self._content_processing(content, post_path=post_path, description=description)

    def _content_processing(self, content: Content, post_path: str = None, description: dict = None) -> None:
        """Сохранятет данные из класса content"""
        content.calculate_dependencies()

        dependencies = content.get_dependencies_by_dict()
        data = content.get_data()

        if not data:
            return
        
        if post_path:
            storage = Storage(data, dependencies, post_path=post_path)
        else:    
            storage = Storage(data, dependencies, key_word=self.key_word)
            self.main_storage = storage
            self.main_content = content

        using_descruption = description if description else self.full_description
        
        storage.save(using_descruption)