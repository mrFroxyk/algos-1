import time
from collections.abc import Callable
from functools import wraps


def timer(func: Callable) -> Callable:
    """Calcuate function runtime."""
    @wraps(func)
    def wrapper(*args, **kwargs):  # noqa: ANN202
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {execution_time} seconds")  # noqa: T201
        return result
    return wrapper
