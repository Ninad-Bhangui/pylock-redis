from typing import Callable
from typing import TypeVar
import functools
import time


T = TypeVar("T")


def retry(
    retries: int, sleep_seconds: int
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(retries):
                result = func(*args, **kwargs)
                if result:
                    return result
                if attempt < retries - 1:
                    time.sleep(sleep_seconds)

            raise Exception(f"Function {func.__name__} failed after {retries} retries")

        return wrapper

    return decorator
