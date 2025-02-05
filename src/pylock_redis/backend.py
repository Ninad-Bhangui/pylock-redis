from typing import Protocol
from redis import Redis


class Backend(Protocol):
    def lock(self): ...
    def unlock(self): ...


class RedisBackend:
    def __init__(self, client: Redis[str]) -> None:
        self.client: Redis[str] = client

    def ping(self):
        return self.client.ping()

    def lock(self):
        pass
