import smtplib
import ssl
from typing import List, Optional

import structlog

from inventory_scan.config import scans_metadata
from inventory_scan.notifier import Notifier


class Emailer(object):
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        subject: str,
        recipients: List[str],
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.subject = subject
        self.recipients = recipients

    def send_message(self, message: str):
        # Avoid scrapy mailsender: https://github.com/scrapy/scrapy/issues/3478
        # Modification of SO: https://stackoverflow.com/questions/57715289/how-to-fix-ssl-sslerror-ssl-wrong-version-number-wrong-version-number-ssl
        context = ssl.create_default_context()

        with smtplib.SMTP(
            host=self.host,
            port=self.port,
        ) as server:
            server.starttls(context=context)
            server.login(self.user, self.password)
            message = "\n".join([f"Subject: {self.subject}", message])
            server.sendmail(
                from_addr=self.user,
                to_addrs=self.recipients,
                msg=message,
            )


class EmailNotifier(Notifier):
    def __init__(
        self,
        emailer: Emailer,
        body_template: str,
        logger: Optional[structlog.stdlib.BoundLogger] = None,
    ):
        self.emailer = emailer
        self.body_template = body_template
        self.body = []
        self.logger = (
            logger
            if logger is not None
            else structlog.get_logger(self.__class__.__name__)
        )

    def on_close(self):
        if len(self.body) > 0:
            self.logger.info("sending mail", items=len(self.body))
            self.emailer.send_message("\n".join(self.body))

    def notify(self, url: str, price: str, availability: bool):
        if availability:
            metadata = scans_metadata.get(url, {})
            metadata = {k: v for k, v in metadata.items() if k != "url"}
            self.body.append(
                self.body_template.format(
                    url=url,
                    price=price,
                    availability=availability,
                    **metadata,
                )
            )
