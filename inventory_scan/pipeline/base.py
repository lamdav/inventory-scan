from abc import ABC, abstractmethod

from scrapy import Item, Spider
from scrapy.crawler import Crawler


class ScrapyPipeline(ABC):
    def open_spider(self, spider: Spider):
        pass

    def close_spider(self, spider: Spider):
        pass

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        pass

    @abstractmethod
    def process_item(self, item: Item, spider: Spider) -> Item:
        pass
