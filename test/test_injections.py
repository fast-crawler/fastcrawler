# pylint: skip-file

import pytest

from fastcrawler.utils import Depends, _Depends, dependency_injector


def test_sync_dependency_injection():
    global outer_sync_value
    outer_sync_value = 0

    def outer_changer():
        global outer_sync_value
        outer_sync_value += 2
        return outer_sync_value

    @dependency_injector
    def inner_func(result: int = Depends(outer_changer), *args):
        for number in args:
            result += number
        return result

    # simple sync test
    inner_func()
    assert outer_sync_value == 2

    # Arg test and cache=True
    result = inner_func(Depends(outer_changer, use_cache=True), 0, 0, 1)
    assert outer_sync_value == 4
    assert result == outer_sync_value + 1


@pytest.mark.asyncio
async def test_async_dependency_injection():
    global out_async_value
    out_async_value = 0

    async def outer_changer():
        global out_async_value
        out_async_value += 2
        return out_async_value

    @dependency_injector
    async def inner_func(result: int = Depends(outer_changer), *args):
        for number in args:
            result += number
        return result

    # simple async test
    await inner_func()
    assert out_async_value == 2

    # Arg test and cache=True
    result = await inner_func(Depends(outer_changer, use_cache=True), 0, 0, 1)
    assert out_async_value == 4
    assert result == out_async_value + 1


def test_repr_depends():
    def inner():
        ...

    repr = Depends(inner).__repr__()
    assert type(repr) == str
    assert "_Depends(inner, use_cache=False)" == repr


def test_Depends_init():
    def dep():
        return "dependency"

    _dep = _Depends(dep, use_cache=True)

    assert _dep.dependency == dep
    assert _dep.use_cache is True


@pytest.mark.asyncio
async def test_Depends_async_eval():
    async def dep():
        return "async_dependency"

    _dep = _Depends(dep)
    result = await _dep.async_eval()

    assert result == "async_dependency"


def test_Depends_sync_eval():
    def dep():
        return "sync_dependency"

    _dep = _Depends(dep)
    result = _dep.sync_eval()

    assert result == "sync_dependency"


@pytest.mark.asyncio
async def test_Depends_inject_async():
    async def dep():
        return "async_dependency"

    _dep = _Depends(dep)
    result = await _Depends.inject(_dep)

    assert result == "async_dependency"


@pytest.mark.asyncio
async def test_Depends_inject_sync():
    def dep():
        return "sync_dependency"

    _dep = _Depends(dep)
    result = await _Depends.inject(_dep)

    assert result == "sync_dependency"


def test_dependency_injector_sync():
    @dependency_injector
    def func(dep=Depends(lambda: "sync_dependency")):
        return dep

    result = func()

    assert result == "sync_dependency"


def test_Depends():
    def dep():
        return "dependency"

    result = Depends(dep)

    assert isinstance(result, _Depends)
    assert result.dependency == dep


@pytest.mark.asyncio
async def test_Depends_inject_with_Depends_in_args_async():
    async def dep():
        return "async_dependency"

    async def func(dep1=Depends(dep, use_cache=True), dep2=Depends(dep, use_cache=False)):
        return dep1, dep2

    _dep = _Depends(func)
    result1, result2 = await _Depends.inject(_dep)

    assert result1 == "async_dependency"
    assert result2 == "async_dependency"


@pytest.mark.asyncio
async def test_Depends_inject_with_Depends_in_args_sync():
    def dep():
        return "sync_dependency"

    def func(dep1=Depends(dep, use_cache=True), dep2=Depends(dep, use_cache=False)):
        return dep1, dep2

    _dep = _Depends(func)
    result1, result2 = await _Depends.inject(_dep)

    assert result1 == "sync_dependency"
    assert result2 == "sync_dependency"


@pytest.mark.asyncio
async def test_dependency_injector_with_Depends_in_args_async():
    @dependency_injector
    async def func(
        dep1=Depends(lambda: "async_dependency1", use_cache=True),
        dep2=Depends(lambda: "async_dependency2", use_cache=False),
    ):
        return dep1, dep2

    result1, result2 = await func()
    assert result1 == "async_dependency1"
    assert result2 == "async_dependency2"


def test_dependency_injector_with_Depends_in_args_sync():
    @dependency_injector
    def func(
        dep1=Depends(lambda: "sync_dependency1", use_cache=True),
        dep2=Depends(lambda: "sync_dependency2", use_cache=False),
    ):
        return dep1, dep2

    result1, result2 = func()

    assert result1 == "sync_dependency1"
    assert result2 == "sync_dependency2"
