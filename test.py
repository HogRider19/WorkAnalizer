
from manager import Manager


params = {'city': False, 'exp': True, 'schedule': True}
manager = Manager('Переводчик', count_page=1, info=True, params=params)

manager.analysis()

