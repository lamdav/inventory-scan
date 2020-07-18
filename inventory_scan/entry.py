import logging
import sys
from dataclasses import dataclass
from typing import List

import click
import structlog
from scrapy.crawler import CrawlerProcess
from slack import WebClient

from inventory_scan.config import scans_metadata, settings
from inventory_scan.handler import AmazonHandler, BestBuyHandler
from inventory_scan.notifier import (
    ConsoleNotifier,
    Emailer,
    EmailNotifier,
    SlackNotifier,
)
from inventory_scan.spider import InventorySpider


@dataclass
class Context(object):
    debug: bool
    logger: structlog.stdlib.BoundLogger


@click.group()
@click.option(
    "--debug",
    "-d",
    help="Enable debug logging",
    type=bool,
    is_flag=True,
    show_default=True,
    default=False,
)
@click.pass_context
def inv(context: click.Context, debug: bool):
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if debug else logging.INFO,
    )
    structlog.configure_once(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    context.obj = Context(debug=debug, logger=structlog.get_logger(),)


_notifiers = {
    "console": ConsoleNotifier(),
    "email": EmailNotifier(
        emailer=Emailer(
            host=settings.get("email.smtp.host"),
            port=settings.get("email.smtp.port"),
            user=settings.get("email.smtp.user"),
            password=settings.get("email.smtp.password"),
            subject=settings.get("email.subject", "No Subject"),
            recipients=settings.get("email.recipients"),
        ),
        body_template=settings.get(
            "email.body_template", "{availability} {price} {url}"
        ),
    ),
    "slack": SlackNotifier(
        client=WebClient(token=settings.get("slack.token"),),
        channel=settings.get("slack.channel"),
        message_template=settings.get("slack.message_template"),
    ),
}


@inv.command()
@click.option(
    "--notifier",
    "-n",
    multiple=True,
    help="Channels to receive messages of inventory.",
    type=click.Choice(_notifiers.keys()),
    show_default=True,
    default=("console",),
)
@click.pass_obj
def scan(context: Context, notifier: List[str]):
    notifiers = [_notifiers.get(n) for n in notifier]

    crawler = CrawlerProcess(
        settings={
            "LOG_LEVEL": logging.DEBUG if context.debug else logging.ERROR,
            "ITEM_PIPELINES": {"inventory_scan.pipeline.NotifierPipeline": 1},
            "NOTIFIERS": notifiers,
        }
    )
    crawler.crawl(
        InventorySpider,
        name="inventory_spider",
        start_urls=list(scans_metadata.keys()),
        handlers=[AmazonHandler(), BestBuyHandler()],
    )
    crawler.start()


if __name__ == "__main__":
    inv()
