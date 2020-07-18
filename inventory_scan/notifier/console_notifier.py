from typing import Optional

import structlog

from inventory_scan.config import scans_metadata
from inventory_scan.notifier import Notifier


class ConsoleNotifier(Notifier):
    def __init__(self, logger: Optional[structlog.stdlib.BoundLogger] = None):
        self.logger = (
            logger
            if logger is not None
            else structlog.getLogger(self.__class__.__name__)
        )

    def notify(self, url: str, price: str, availability: bool):
        if availability:
            metadata = scans_metadata.get(url, {})
            self.logger.info(
                f"{metadata.get('name', 'Item')} is available from {metadata.get('store', '???')} ({price}) at {url}"
            )
