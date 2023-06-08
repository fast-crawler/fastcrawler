import pytest

from fastcrawler.utils import Depends, dependency_injector


def test_sync_depedencacy_injection():
    global outer_sync_value
    outer_sync_value = 0

    def outer_changer():
        print("HEY!")
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
    assert result == outer_sync_value+1


@pytest.mark.asyncio
async def test_async_depedencacy_injection():
    global out_async_value
    out_async_value = 0

    async def outer_changer():
        print("HEY!")
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
    assert result == out_async_value+1


def test_repr_depends():
    def inner(): ...

    repr = Depends(inner).__repr__()
    assert type(repr) == str
    assert "Depends(inner, use_cache=False)" == repr
