from abc import abstractmethod, ABCMeta
import requests


class Webhook(metaclass=ABCMeta):
    @abstractmethod
    def sendNotification(self, message: str) -> None:
        raise NotImplementedError


class Discord(Webhook):

    def __init__(self, *, webhook_id: str, webhook_token: str):
        self.webhook_url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"

    def sendNotification(self, message: str) -> None:
        requests.post(self.webhook_url, json={"content": message})
