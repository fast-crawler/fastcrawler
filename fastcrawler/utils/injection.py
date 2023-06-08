import asyncio
from typing import Callable, Any
from functools import wraps
import inspect


class Depends:
    """Dependancy injection to run callable as a dependency
    """
    def __init__(
        self, dependency: Callable[..., Any] | None = None,
        *,
        use_cache: bool = False
    ):
        self.dependency = dependency
        self.use_cache = use_cache
        self.result = ...

    async def async_eval(self):
        """Run async callable dependnecy and store it as cache entry
        """
        if self.result is ...:
            self.result = await self.dependency()
        return self.result

    def sync_eval(self):
        """Run sync callable dependency and store it as cache entry
        """
        if self.result is ...:
            self.result = self.dependency()
        return self.result

    def __repr__(self) -> str:
        """ Represents the callable dependency
        """
        attr = getattr(
            self.dependency, "__name__", type(self.dependency).__name__
        )
        cache = "" if self.use_cache else ", use_cache=False"
        return f"{self.__class__.__name__}({attr}{cache})"


def dependency_injector(func):
    """Wrapper to evaluate dependencies and save them either as cached or non-cached

    works for both async and sync
    """
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            for name, value in bound.arguments.items():
                if isinstance(value, Depends):
                    if value.use_cache:
                        bound.arguments[name] = await value.async_eval()
                    else:
                        new_dependency = Depends(value.dependency, use_cache=False)
                        bound.arguments[name] = await new_dependency.async_eval()
                else:
                    bound.arguments[name] = value

            return await func(*bound.args, **bound.kwargs)

    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            for name, value in bound.arguments.items():
                if isinstance(value, Depends):
                    if value.use_cache:
                        bound.arguments[name] = value.sync_eval()
                    else:
                        new_dependency = Depends(value.dependency, use_cache=False)
                        bound.arguments[name] = new_dependency.sync_eval()
                else:
                    bound.arguments[name] = value

            return func(*bound.args, **bound.kwargs)

    return wrapper
