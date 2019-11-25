from unittest import TestCase
import requests
from bs4 import BeautifulSoup
from parser import ParseAirforce


class TestParseAirforce(TestCase):

    def test_get_data_site(self, url='https://www.airforce-technology.com/news/page/1/'):
        self.assertIsNotNone(requests.get(url).text)

    def test_get_articles(self, url='https://www.airforce-technology.com/news/page/1/'):
        article = BeautifulSoup(ParseAirforce().get_data_site(url), 'lxml').find('ul',
                                                                                 {
                                                                                     'class': 'category_list_new pal list'}).findAll(
            href=True)
        self.assertIsNotNone(article)
