from typing import Callable
from typing import TypeVar
import functools
import time


T = TypeVar("T")


def exponential_retry(
    retries: int, backoff_factor: int
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(retries):
                result = func(*args, **kwargs)
                if result:
                    return result
                if attempt < retries - 1:
                    sleep_seconds: int = 1 * (backoff_factor**attempt)
                    time.sleep(sleep_seconds)

            raise Exception(f"Function {func.__name__} failed after {retries} retries")

        return wrapper

    return decorator
