from typing import Any, List, Optional

from itemadapter import ItemAdapter
from scrapy import Item, Spider
from scrapy.crawler import Crawler

from inventory_scan.pipeline.base import ScrapyPipeline


class NotifierPipeline(ScrapyPipeline):
    def __init__(self, notifiers: Optional[List[Any]] = None):
        self.notifiers = notifiers if notifiers is not None else []

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(notifiers=crawler.settings.get("NOTIFIERS", []))

    def process_item(self, item: Item, spider: Spider) -> Item:
        adapter = ItemAdapter(item)
        for notifier in self.notifiers:
            notifier.notify(
                adapter.get("url"), adapter.get("price"), adapter.get("availability")
            )
        return item

    def close_spider(self, spider: Spider):
        for notifier in self.notifiers:
            notifier.on_close()
