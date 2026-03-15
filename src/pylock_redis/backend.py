from datetime import timedelta
from typing import Protocol
from redis import Redis


class Backend(Protocol):
    def lock(
        self, identifier: str, identifier_value: str, lock_validity_time: timedelta
    ) -> bool: ...
    def unlock(self, identifier: str, identifier_value: str) -> bool: ...


class RedisBackend:
    def __init__(self, client: Redis) -> None:
        self.client: Redis = client
        unlock_lua = """
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("del",KEYS[1])
else
    return 0
end
"""
        self._unlock_script = self.client.register_script(unlock_lua)

    def ping(self):
        return self.client.ping()

    def lock(
        self, identifier: str, identifier_value: str, lock_validity_time: timedelta
    ) -> bool:
        res = self.client.set(
            identifier, identifier_value, nx=True, px=lock_validity_time
        )
        if res:
            return res
        return False

    def unlock(self, identifier: str, identifier_value: str):
        res = self._unlock_script(keys=[identifier], args=[identifier_value])
        if res:
            return res
        return False
