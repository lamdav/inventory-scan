from typing import List, Optional

import structlog
from scrapy import Spider

from inventory_scan.handler import Handler


class InventorySpider(Spider):
    def __init__(
        self,
        name: Optional[str] = None,
        start_urls: Optional[List[str]] = None,
        handlers: Optional[List[Handler]] = None,
        logger: Optional[structlog.stdlib.BoundLogger] = None,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.start_urls = [] if start_urls is None else start_urls
        self.handlers = handlers if handlers is not None else []
        self.struct_logger = (
            logger
            if logger is not None
            else structlog.get_logger(self.__class__.__name__)
        )

    def parse(self, response):
        results = [
            handler.handle(response)
            for handler in self.handlers
            if handler.can_handle(response.url)
        ]
        results = [result for result in results if result is not None]
        self.struct_logger.debug("parsed results", count=len(results), results=results)
        for result in results:
            yield result.dict()
