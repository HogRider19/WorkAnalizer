from src.manager import Manager


class Assistant(object):

    detail = {}

    def __init__(self) -> None:
        self.position_tree = 0
        self.tree = {
            0: {'message': '\nВведите ключевое слово: ', 'key': 'keyword', 'convert': lambda x: x},
            1: {'message': '\nВведите количество страниц: ', 'key': 'page_count', 'convert': lambda x: int(x)},
            2: {'message': '\nГород для поиска(id/None): ', 'key': 'area',
                'convert': lambda x: None if x.lower() == 'none' or x == '' else x},
            3: {'message': '\nСобирать данные по опыту(да/нет): ', 'key': 'exp',
                'convert': lambda x: True if x.lower() == 'да' else False},
            4: {'message': '\nСобирать данные по графику работы(да/нет): ', 'key': 'schedule',
                'convert': lambda x: True if x.lower() == 'да' else False},
            5: {'message': '\nВывод информации в консоль(да/нет): ', 'key': 'info',
                'convert': lambda x: True if x.lower() == 'да' else False},
        }

    def start(self) -> None:
        """Начинает диалог"""
        self.position_tree = 0
        return self.tree[self.position_tree]['message']

    def next(self, message: str) -> str:
        """Следующий шаг диалога"""
        key = self.tree[self.position_tree]['key']
        convert = self.tree[self.position_tree]['convert']

        self.detail.update({key: convert(message)})

        self.position_tree += 1
        if self.position_tree <= max(self.tree.keys()):
            return self.tree[self.position_tree]['message']
        self.end()

    def end(self) -> None:
        """Завершает диалог"""
        params = {'exp': self.detail['exp'],
                  'schedule': self.detail['schedule'], }
        manager = Manager(
            self.detail['keyword'], count_page=self.detail['page_count'], info=self.detail['info'], params=params)

        manager.analysis(area_id=self.detail['area'])
