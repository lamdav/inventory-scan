from urllib.parse import urlparse

from scrapy.http import Response

from inventory_scan.handler import Handler, Result


class AmazonHandler(Handler):
    def can_handle(self, url: str) -> bool:
        hostname = urlparse(url).hostname
        return hostname is not None and (
            hostname == "www.amazon.com" or hostname == "smile.amazon.com"
        )

    def handle(self, response: Response) -> Result:
        price = "UNKNOWN"
        availability = response.css("div[id=outOfStock]").get() is None
        if availability:
            # Check if it is available new
            price = response.css("span[id=price_inside_buybox]::text").get()
            if not price:
                # Check if it is available used
                price = response.css("div[id=buyNew_noncbb]").css("span::text").get()
            if isinstance(price, str):
                price = price.strip()
        return Result(url=response.url, price=price, availability=availability)
