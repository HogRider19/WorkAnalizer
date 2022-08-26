
class Content(object):

    data = list()
    city_quantity = list()
    salaries_quantity = list()
    skills_quantity = list()

    def __init__(self, data=[]) -> None:
        self.data = data

    def set_data(self, data: list):
        if not isinstance(data, list):
            raise ArithmeticError("The right operand must be of type list")

        self.data = data

    def filter(self) -> None:
        """Отбирает определенные поля из словаря с вакансиями"""
        required_fields = ['id', 'name', 'published_at',
                           'alternate_url', 'description', 'key_skills']

        filter_data = []
        for vacancy in self.data:

            filter_data_once = {}
            for required_field in required_fields:
                filter_data_once[required_field] = vacancy[required_field]

            filter_data_once['sal_from'] = vacancy['salary']['from'] if 'from' in vacancy['salary'] else None
            filter_data_once['sal_to'] = vacancy['salary']['to'] if 'to' in vacancy['salary'] else None
            filter_data_once['currency'] = vacancy['salary']['currency'] if 'currency' in vacancy['salary'] else None
            filter_data_once['city'] = vacancy['address']['city'] if 'city' in vacancy['address'] else None
            filter_data_once['address'] = vacancy['address']['street'] if 'street' in vacancy['address'] else None
            filter_data_once['company'] = vacancy['employer']['name'] if 'name' in vacancy['employer'] else None
            filter_data_once['experience'] = vacancy['experience']['name'] if 'name' in vacancy['experience'] else None
            filter_data_once['schedule'] = vacancy['schedule']['name'] if 'name' in vacancy['schedule'] else None

            filter_data_once['key_skills'] = []
            if vacancy['key_skills'] is not None:
                for key_skill in vacancy['key_skills']:
                    filter_data_once['key_skills'].append(key_skill['name'])

            filter_data.append(filter_data_once)

        self.data = filter_data

    def calculate_dependencies(self) -> None:
        """Вычисляет зависимости для построения графиков"""
        self._calculatet_city_quantity()
        self._calculate_salaries_quantity()
        self._calculate__skills_quantity()

    def get_dependencies_by_dict(self) -> dict:
        """Возвращает все зависимости в виде словаря"""
        return {
            'city': self.city_quantity,
            'salary': self.salaries_quantity,
            'skill': self.skills_quantity,
        }

    def _calculatet_city_quantity(self, percent=0.5) -> list:
        """Рассчитывает рейтинг городов по количеству вакансий"""
        cities = [city for city in list(
            map(lambda x: x['city'], self.data)) if city]
        cities_set = list(set(cities))

        dependence = {}
        for city_name in cities_set:
            count = cities.count(city_name)
            if count/len(self.data)*100 > percent:
                dependence.update({city_name: count})

        items = dependence.items()
        items_sorted = sorted(list(map(lambda x: [x[1], x[0]], items)))
        counts = list(map(lambda x: x[0], items_sorted))
        groups = list(map(lambda x: x[1], items_sorted))

        self.city_quantity = [groups, counts]

    def _calculate_salaries_quantity(self, min_border=10000, max_border=400000, step=10000) -> list:
        """Рассчитывает зависимость зарплаты от количества вакансий"""
        salaries = self._get_unpacking_salary()

        dependence = []
        groups = []

        for lower_step in range(min_border, max_border, step):
            dependence_step = 0
            groups.append(f'{round(lower_step/1000)}-{round((lower_step+step)/1000)}')
            for salary in salaries:
                if lower_step < salary <= lower_step + step:
                    dependence_step += 1
            dependence.append(dependence_step)

        for i in range(len(dependence)):
            dependence[i] = dependence[i]*100/len(salaries)

        self.salaries_quantity = [groups, dependence]

    def _calculate__skills_quantity(self) -> list:
        """Рассчитывает распределение ключевых навыков по частоте упоминантя в вкансиях"""
        key_skills = []
        for items in list(map(lambda x: x['key_skills'], self.data)):
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
        items_sorted = sorted(list(map(lambda x: [x[1], x[0]], items)))
        counts = list(map(lambda x: x[0]/total_vacancies*100, items_sorted))
        groups = list(map(lambda x: x[1], items_sorted))

        self.skills_quantity = [groups, counts]

    def _get_unpacking_salary(self) -> list:
        """Возвращвет зарплаты в виде списка"""
        salary = []
        for vacancy in self.data:

            if vacancy['currency'] == 'RUR':
                salary_from = vacancy['sal_from'] if isinstance(
                    vacancy['sal_from'], int) else None
                salary_to = vacancy['sal_to'] if isinstance(
                    vacancy['sal_to'], int) else None

                if salary_from:
                    salary.append(salary_from)

                if salary_to:
                    salary.append(salary_to)

        return salary.sort()

    def __add__(self, other):
        if not isinstance(other, (Content, list)):
            raise ArithmeticError(
                "The right operand must be of type Content or list")

        other_data = other if isinstance(other, list) else other.data
        return Content(self.data + other_data)
