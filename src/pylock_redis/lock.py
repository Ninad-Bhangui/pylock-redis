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
    backoff_factor: int

    def __init__(
        self,
        backend: Backend,
        identifier: str,
        lock_validity_time: timedelta,
        max_retries: int = 10,
        backoff_factor: int = 2,
    ) -> None:
        self.backend = backend
        self.identifier = identifier
        self.identifier_value = str(uuid4())
        self.lock_validity_time = lock_validity_time
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def __enter__(self):
        @exponential_retry(self.max_retries, self.backoff_factor)
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
