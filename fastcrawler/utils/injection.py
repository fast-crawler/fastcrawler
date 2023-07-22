import asyncio
import inspect
from functools import wraps
from typing import Any, Callable


class _Depends:
    """Dependancy injection to run callable as a dependency"""

    def __init__(
        self,
        dependency: Callable[..., Any],
        use_cache: bool = False,
        *args,
        **kwargs,
    ):
        self.dependency = dependency
        self.use_cache = use_cache
        self.result = ...
        self.args = args
        self.kwargs = kwargs

    async def async_eval(self):
        """Run async callable dependnecy and store it as cache entry"""
        if self.result is ...:
            if asyncio.iscoroutinefunction(self.dependency):
                self.result = await self.dependency()
            else:
                self.result = self.dependency()
        return self.result

    def sync_eval(self):
        """Run sync callable dependency and store it as cache entry"""
        if self.result is ...:
            self.result = self.dependency()
        return self.result

    def __repr__(self) -> str:
        """Represents the callable dependency"""
        attr = getattr(
            self.dependency,
            "__name__",
            type(self.dependency).__name__,
        )
        cache = "" if self.use_cache else ", use_cache=False"
        return f"{self.__class__.__name__}({attr}{cache})"

    @staticmethod
    async def inject(func: "_Depends"):
        if asyncio.iscoroutinefunction(func.dependency):
            sig = inspect.signature(func.dependency)
            bound = sig.bind_partial(*func.args, **func.kwargs)
            bound.apply_defaults()
            for name, value in bound.arguments.items():
                if isinstance(value, _Depends):
                    if value.use_cache:
                        bound.arguments[name] = await value.async_eval()
                    else:
                        new_dependency: _Depends = Depends(value.dependency, use_cache=False)
                        bound.arguments[name] = await new_dependency.async_eval()
                else:
                    bound.arguments[name] = value
            return await func.dependency(*bound.args, **bound.kwargs)

        else:
            sig = inspect.signature(func.dependency)
            bound = sig.bind_partial(*func.args, **func.kwargs)
            bound.apply_defaults()
            for name, value in bound.arguments.items():
                if isinstance(value, _Depends):
                    if value.use_cache:
                        bound.arguments[name] = value.sync_eval()
                    else:
                        new_dependency: _Depends = Depends(value.dependency, use_cache=False)
                        bound.arguments[name] = new_dependency.sync_eval()
                else:
                    bound.arguments[name] = value
            return func.dependency(*bound.args, **bound.kwargs)


def dependency_injector(func):
    """Wrapper to evaluate dependencies and save them either as cached or non-cached

    works for both async and sync
    """
    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            for name, value in bound.arguments.items():
                if isinstance(value, _Depends):
                    if value.use_cache:
                        bound.arguments[name] = await value.async_eval()
                    else:
                        new_dependency: _Depends = Depends(value.dependency, use_cache=False)
                        bound.arguments[name] = await new_dependency.async_eval()
                else:
                    bound.arguments[name] = value

            return await func(*bound.args, **bound.kwargs)

        return async_wrapper

    else:

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            for name, value in bound.arguments.items():
                if isinstance(value, _Depends):
                    if value.use_cache:
                        bound.arguments[name] = value.sync_eval()
                    else:
                        new_dependency: _Depends = Depends(value.dependency, use_cache=False)
                        bound.arguments[name] = new_dependency.sync_eval()
                else:
                    bound.arguments[name] = value

            return func(*bound.args, **bound.kwargs)

        return sync_wrapper


def Depends(
    dependency: Callable[..., Any],
    *,
    use_cache: bool = False,
) -> Any:
    """The reason that an object was initiated from class, and the class wasn't called directly
    is that because class __init__ method is returning only the instance of that class,
    and that's not what we want, we want to assign this to another type (ANY), so I should
    be using a function as interface to avoid IDE's error in type annotation or mypy.
    """
    return _Depends(dependency=dependency, use_cache=use_cache)
