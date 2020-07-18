from typing import Optional
from urllib.parse import urlparse

import structlog

from inventory_scan.handler.base import Handler, Result


class BestBuyHandler(Handler):
    def __init__(self, logger: Optional[structlog.stdlib.BoundLogger] = None):
        self.logger = (
            logger
            if logger is not None
            else structlog.get_logger(self.__class__.__name__)
        )

    def can_handle(self, url: str) -> bool:
        hostname = urlparse(url).hostname
        return hostname is not None and hostname.lower() == "www.bestbuy.com"

    def handle(self, response) -> Result:
        price = (
            response.css("div.priceView-hero-price")
            .css(".priceView-customer-price")
            .css("span[aria-hidden=true]::text")
            .get()
        )
        availability = (
            response.css("button.add-to-cart-button::text").get().lower()
            == "add to cart"
        )
        return Result(url=response.url, price=price, availability=availability)
