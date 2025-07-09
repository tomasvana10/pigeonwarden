import time
from functools import wraps
from typing import Callable, Any

def cooldown(seconds: float, cooldown_return_value: Any = None) -> Callable:
    last_called: dict[tuple[Callable, tuple[Any, ...]], float] = {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.time()
            key = (func, args)
            if key in last_called and now - last_called[key] < seconds:
                return cooldown_return_value
            last_called[key] = now
            return func(*args, **kwargs)
        return wrapper
    return decorator

@cooldown(5, cooldown_return_value=False)
def func() -> bool:
    print("doing something")
    return True

print(func())  # True
print(func())  # False (if within 5 seconds)
