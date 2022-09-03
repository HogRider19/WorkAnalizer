from src.manager import Manager


params = {'exp': True, 'schedule': True,}
manager = Manager('Доставщик', count_page=3, info=True, params=params)

manager.analysis(area_id=2)

