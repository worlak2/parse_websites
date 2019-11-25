from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from multiprocessing import Pool
import multiprocessing.pool
from database import insert, db, check_data
import os
import sys
from pathlib import Path
import shutil
import requests


class NoDaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass

    daemon = property(_get_daemon, _set_daemon)


class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


class BaseParse(ABC):
    _process_count = 20

    @property
    def process_count(self):
        return self._process_count

    @process_count.setter
    def process_count(self, value):
        if isinstance(value, str):
            self._process_count = int(value)
        elif isinstance(value, int):
            self._process_count = value
        else:
            raise ValueError(f'Failed parse value {value}. Failed format.')

    @abstractmethod
    def get_data_site(self, url):
        pass

    @abstractmethod
    def get_articles(self, url):
        pass

    @abstractmethod
    def parse_article(self, url):
        pass

    @abstractmethod
    def parse_all_data(self):
        pass

    @abstractmethod
    def parse_new(self):
        pass

    @staticmethod
    def insert_to_database(data):
        with db.atomic() as transaction:
            try:
                for i in data: insert(**i)
            except Exception as e:
                print(e)
                transaction.rollback()

    def parse_data(self, url):
        parsed_article = self.get_articles(url)
        if parsed_article:
            with Pool(self._process_count) as p:
                release = p.map(self.parse_article, [{'url': i['href'], 'title': i.text} for i in parsed_article])
            self.insert_to_database(release)


class BaseParseArticle(ABC):

    @abstractmethod
    def parse_article(self, args, data):
        pass


class BaseImageSave:
    def __init__(self, path):
        self.base_path = path

    @staticmethod
    def rename_image(article):
        return f'{hash(article)}.jpg'

    def download_image(self, url, article):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            path = Path("media/images/") / self.base_path / article
            os.makedirs(path, exist_ok=True)
            path = path / self.rename_image(article)
            with open(path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            return path
        else:
            return None

    def save_image(self, url, article):
        image = self.download_image(url, article)
        return image


class ParseAirforceArticle(BaseParseArticle):

    def parse_article(self, args, data):
        parsed_data = data.find('div', {
            'class': 'post-content cf'}).findAll('p')

        parsed_list = [i.text for i in parsed_data[:-1]]
        parsed_list[-1] = parsed_list[-1][:parsed_list[-1].find('\n')]
        date_publication = data.find('div', {'class': 'article-date'})

        image = data.find('div', {'class': 'share-container'}).findAll('img')
        image = image[0] if len(image) > 1 else None
        work_with_image = BaseImageSave('Airforce').save_image(image['src'], args['title']) if image else None

        return {'url': args['url'], 'title': args['title'], 'images_path': work_with_image,
                'data_site': ''.join(parsed_list), 'date_upload': date_publication.text}


class ParseAirforce(BaseParse):

    def get_data_site(self, url):
        return requests.get(url).text

    def get_articles(self, url):
        article = BeautifulSoup(self.get_data_site(url), 'lxml').find('ul',
                                                                      {'class': 'category_list_new pal list'}).findAll(
            href=True)
        return article if len(article) > 0 else None

    def parse_article(self, args):
        data = BeautifulSoup(self.get_data_site(url=args['url']), 'lxml')
        parsed_article = ParseAirforceArticle().parse_article(args, data)
        return parsed_article

    def parse_new(self):
        sys.setrecursionlimit(25000)
        to_parse = []
        with Pool(self._process_count) as p:
            parsed_articles = p.map(self.get_articles,
                                    ['https://www.airforce-technology.com/news/page/{0}/'.format(i) for i in
                                     range(1, 50)])
            for i in parsed_articles:
                for j in i:
                    if not check_data(j['href']):
                        to_parse.append(j)
            release = p.map(self.parse_article, [{'url': i['href'], 'title': i.text} for i in to_parse])
        self.insert_to_database(release)

    def parse_all_data(self):
        pool = MyPool(6)
        pool.map(self.parse_data,
                 [f'https://www.airforce-technology.com/news/page/{i}/' for i in range(1, 50)])
        pool.close()
        pool.join()


if __name__ == '__main__':
    result = ParseAirforce()
    # result.parse_all_data()
    result.parse_new()
