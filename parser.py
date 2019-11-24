from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from multiprocessing import Pool
import requests


class BaseParse(ABC):

    @abstractmethod
    def get_data_site(self):
        pass

    @abstractmethod
    def get_articles(self):
        pass

    @abstractmethod
    def parse_data(self):
        pass

    @abstractmethod
    def parse_article(self, url):
        pass

    @abstractmethod
    def download_image(self, url):
        pass

    def insert_to_database(self):
        pass


class ParseAirforce(BaseParse):
    def __init__(self, url):
        self.url = url
        self._process_count = 20

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

    def get_data_site(self, addition_url=None):
        if addition_url:
            return requests.get(addition_url).text
        return requests.get(self.url).text

    def get_articles(self):
        article = BeautifulSoup(self.get_data_site(), 'lxml').find('ul',
                                                                   {'class': 'category_list_new pal list'}).findAll(
            href=True)
        return article if len(article) > 0 else None

    def download_image(self, url):
        pass

    def parse_article(self, *args):
        data = BeautifulSoup(self.get_data_site(addition_url=args[0]['url']), 'lxml')
        parsed_data = data.find('div', {
            'class': 'post-content cf'}).findAll('p')

        parsed_list = [i.text for i in parsed_data[:-1]]
        parsed_list[-1] = parsed_list[-1][:parsed_list[-1].find('\n')]


        image = data.find('div',{'class':'share-container'}).findAll('img')[0]
        print(image['src'])

        return args[0]['url'], args[0]['title']


    def parse_data(self):
        parsed_article = self.get_articles()
        if parsed_article:
            with Pool(self._process_count) as p:
                release = p.map(self.parse_article, [{'url': i['href'], 'title': i.text} for i in parsed_article])
                print(release)


if __name__ == '__main__':
    result = ParseAirforce('https://www.airforce-technology.com/news/')
    result.parse_data()
