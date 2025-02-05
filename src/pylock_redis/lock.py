from datetime import timedelta
from types import TracebackType
from uuid import uuid4
from .backend import Backend
from .retry import exponential_retry


class Locker:
    backend: Backend
    identifier: str
    identifier_value: str
    lock_validity_time: timedelta
    max_retries: int

    def __init__(
        self,
        backend: Backend,
        identifier: str,
        lock_validity_time: timedelta,
        max_retries: int,
    ) -> None:
        self.backend = backend
        self.identifier = identifier
        self.identifier_value = str(uuid4())
        self.lock_validity_time = lock_validity_time
        self.max_retries = max_retries

    def __enter__(self):
        @exponential_retry(self.max_retries, 2)
        def try_lock():
            return self.backend.lock(
                self.identifier, self.identifier_value, self.lock_validity_time
            )

        if try_lock():
            return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType,
    ):
        self.backend.unlock(self.identifier, self.identifier_value)
