
from manager import Manager


params = {'exp': True, 'schedule': True,}
manager = Manager('C++ developer', count_page=50, info=True, params=params)

manager.analysis(area_id=2)

