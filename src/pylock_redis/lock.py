from types import TracebackType
from .backend import Backend


class Locker:
    backend: Backend

    def __init__(self, backend: Backend) -> None:
        self.backend = backend

    def __enter__(self):
        pass

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType,
    ):
        pass
