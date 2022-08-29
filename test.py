from storage import Storage
from loader import Loader
from content import Content

key_word = 'Developer'

loader = Loader(key_word)
loader.load(30)

data_raw = loader.get_data()

content = Content(data_raw)
content.calculate_dependencies()

dependencies = content.get_dependencies_by_dict()
data = content.get_data()

info = {
    'city': {'name': 'city_quantity', 'tytle': 'Вакансии в городах'},
    'salary': {'name': 'distribution_salaries', 'tytle': 'Зависимость количества вакансий от зарплат'},
    'skill': {'name': 'skills_quantity', 'tytle': 'Востребованность навыков'},
}

storage = Storage(data, dependencies, key_word=key_word)
storage.save(info)
