import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def awaitable(func: Callable[P, R]) -> Callable[P, Coroutine[None, None, R]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper
