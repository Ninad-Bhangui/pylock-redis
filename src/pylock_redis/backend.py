from datetime import timedelta
from typing import Protocol
from redis import Redis


class Backend(Protocol):
    def lock(self, identifier: str, identifier_value: str, lock_validity_time: timedelta)-> bool: ...
    def unlock(self, identifier: str, identifier_value: str)-> bool: ...


class RedisBackend:
    def __init__(self, client: Redis) -> None:
        self.client: Redis = client

    def ping(self):
        return self.client.ping()

    def lock(self, identifier: str, identifier_value: str, lock_validity_time: timedelta)-> bool:
        res = self.client.set(identifier, identifier_value, nx=True,px=lock_validity_time)
        if res:
            return res
        return False
    def unlock(self, identifier: str, identifier_value: str):
        unlock_lua = """
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("del",KEYS[1])
else
    return 0
end
"""
        unlock = self.client.register_script(unlock_lua)
        res = unlock(keys=[identifier], args=[identifier_value])
        if res:
            return res
        return False
