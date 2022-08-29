from storage import Storage
from loader import Loader
from content import Content


class Manager(object):

    main_content = Content()

    def __init__(self, key_word: str, count_page: int, info: bool = True, full_analysis: bool = True) -> None:
        self.key_word = key_word
        self.count_page = count_page
        self.info = info
        self.full_analysis = full_analysis
        self.full_description = {
            'city': {'name': 'city_quantity', 'tytle': 'Вакансии в городах'},
            'salary': {'name': 'distribution_salaries', 'tytle': 'Зависимость количества вакансий от зарплат'},
            'skill': {'name': 'skills_quantity', 'tytle': 'Востребованность навыков'},
        }   

    def analysis(self) -> None:
        """Производит анализ по заданным параметрам"""
        self._main_analysis()
        
        if self.full_analysis:
            self._city_analysis()
            self._exp_analysis()
            self._schedule_analysis()

    def _main_analysis(self) -> None:
        """Производит анализ полностью по всем вакансиям"""
        loader = Loader(self.key_word)
        loader.load(self.count_page, info=self.info)

        data_raw = loader.get_data()

        content = Content(data_raw)
        content.calculate_dependencies()

        dependencies = content.get_dependencies_by_dict()
        data = content.get_data()

        storage = Storage(data, dependencies, key_word=self.key_word)
        storage.save(self.full_description)

    def _city_analysis(self) -> None:
        """Производит анализ с учетом города"""
        pass

    def _exp_analysis(self) -> None: 
        """Производит анализ с учетом опыта работы"""
        pass 

    def _schedule_analysis(self) -> None:
        """Производит анализ с учетом графика работы"""
        pass