import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
import csv
import os


class Storage(object):

    data = list()
    dependencies = dict()
    time_now = ''
    key_word = ''
    main_path = ''

    def __init__(self, data: list, dep: dict, post_path: str = None, key_word: str = None) -> None:
        self.time_now = datetime.datetime.now().strftime('%d_%m_%y_%H_%M')
        self.key_word = key_word
        self.data = data
        self.dependencies = dep
        if post_path:
            self.main_path = f'{post_path}'
        else:
            self.main_path = f'data/[{self.key_word}] {self.time_now}'

        if not os.path.isdir(f'data'):
            os.mkdir('data')

    def save(self, info: dict) -> None:
        """Сохраняет полученные данные"""
        self._create_directory()
        if self.data:
            self._save_vacancies()

        for key in self.dependencies.keys():
            if key in info:
                self._save_plot(self.dependencies[key], info[key]['name'],
                                info[key]['tytle'], split=info[key].get('split', True))

    def get_main_path(self):
        """Возвращает путь к основной директории сохранения"""
        return self.main_path

    def _save_plot(self, data: list, name: str, title: str, path: str = '', split: bool = True) -> None:
        """Созраняет график по указанному пути"""
        split_data = data
        if split:
            split_data = self._split_groups(data, 30)
        mpl.rcParams['font.size'] = 5.0
        plt.figure(clear=True, figsize=(5, 3), dpi=1000)
        plt.bar(split_data[0], split_data[1])
        plt.xticks(rotation=90)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(f'{self.main_path}{path}/{name}.png')
        plt.close()

    def _save_vacancies(self) -> None:
        """Сохраняет собранные вакансии"""
        fieldnames = [
            'name', 'city', 'address',
            'key_skills', 'sal_from', 'sal_to',
            'currency', 'company', 'experience',
            'schedule', 'published_at', 'description',
            'alternate_url', 'id'
        ]
        with open(f'{self.main_path}/vacancies.csv', 'w', newline='', encoding='utf8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            for row in self.data:
                writer.writerow(row)

    def _split_groups(self, group_list, split_len):
        """Обрезает список групп и их значений до указанного количества"""
        if len(group_list[0]) > split_len:
            delta = len(group_list[0]) - split_len
            new_group = group_list[0][delta:]
            new_values = group_list[1][delta:]
            return [new_group, new_values]

        return group_list

    def _create_directory(self) -> None:
        """Создает главную директорию"""
        if not os.path.isdir(f'{self.main_path}'):
            os.mkdir(f'{self.main_path}')
