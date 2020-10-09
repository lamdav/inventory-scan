from typing import Optional

import structlog
from slack import WebClient

from inventory_scan.config import scans_metadata
from inventory_scan.notifier import Notifier


class SlackNotifier(Notifier):
    def __init__(
        self,
        client: WebClient,
        channel: str,
        message_template: str,
        logger: Optional[structlog.stdlib.BoundLogger] = None,
    ):
        self.client = client
        self.channel = channel
        self.message_template = message_template
        self.logger = (
            logger
            if logger is not None
            else structlog.get_logger(self.__class__.__name__)
        )
        self.blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":exclamation: Inventory Scan Alerts :exclamation:",
                },
            },
            {
                "type": "divider",
            },
        ]

    def notify(self, url: str, price: str, availability: bool):
        if availability:
            metadata = scans_metadata.get(url, {"name": "UNKNOWN"})
            metadata = {k: v for k, v in metadata.items() if k != "url"}
            self.logger.info("metadata", metadata=metadata, url=url)
            self.blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": self.message_template.format(
                            url=url, price=price, availability=availability, **metadata
                        ),
                    },
                }
            )

    def on_close(self):
        if len(self.blocks) > 2:
            self.logger.info("sending message to slack", blocks=len(self.blocks))
            self.client.chat_postMessage(
                channel=self.channel,
                blocks=self.blocks,
            )
