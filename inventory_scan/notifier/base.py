from abc import ABC, abstractmethod


class Notifier(ABC):
    def on_close(self):
        pass

    @abstractmethod
    def notify(self, url: str, price: str, availability: bool):
        pass
