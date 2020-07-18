from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel
from scrapy.http import Response


class Result(BaseModel):
    url: str
    price: str
    availability: bool
    extras: Optional[Dict[str, Any]] = {}


class Handler(ABC):
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        pass

    @abstractmethod
    def handle(self, response: Response) -> Result:
        pass
