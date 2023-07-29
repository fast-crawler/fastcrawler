import time

import pytest

from fastcrawler import Depends, Process, Spider
from fastcrawler.schedule import ProcessController, RocketryApplication

from ..shared.core import PersonPage, get_urls

total_crawled = 0


@pytest.mark.asyncio
async def test_spider_depth():
    class MySpider(Spider):
        engine_request_limit = 1
        max_depth = 1
        batch_size = 1
        data_model = PersonPage
        start_url = Depends(get_urls)

        async def save(self, all_data: list[PersonPage]):
            global total_crawled
            total_crawled += 1

    process = Process(
        spider=MySpider(),
        cond="every 1 second",
        controller=ProcessController(app=RocketryApplication()),
    )
    await process.add_spiders()
    assert len(await process.controller.app.get_all_tasks()) == 1
    await process.start(silent=False)
    assert total_crawled == 1, "Depth was not being respected"


@pytest.mark.asyncio
async def test_spider_request_sleep():
    global total_crawled
    total_crawled = 0

    class MySpider(Spider):
        engine_request_limit = 20
        request_sleep_interval = 0.1
        data_model = PersonPage
        start_url = Depends(get_urls)

        async def save(self, all_data: list[PersonPage]):
            global total_crawled
            total_crawled += 1

    start_time = time.time()
    process = Process(
        spider=MySpider(),
        cond="every 1 second",
        controller=ProcessController(app=RocketryApplication()),
    )
    await process.add_spiders()
    assert len(await process.controller.app.get_all_tasks()) == 1
    await process.start(silent=False)
    end_time = time.time()
    execution_time = end_time - start_time

    assert (
        execution_time >= 2
    ), f"Execution took {execution_time} seconds, which is not logner than 2 seconds."
