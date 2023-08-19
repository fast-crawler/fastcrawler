import asyncio

import pytest

from fastcrawler import Depends, Process, Spider
from fastcrawler.schedule import ProcessController, RocketryApplication

from ..shared.core import PersonPage, get_urls

total_crawled = 0


class MySpider(Spider):
    engine_request_limit = 1
    data_model = PersonPage
    start_url = Depends(get_urls)

    async def save(self, all_data: list[PersonPage]):
        global total_crawled
        total_crawled += 1


@pytest.mark.asyncio
async def test_process():
    process = Process(
        spider=MySpider(),
        cond="every 1 second",
        controller=ProcessController(app=RocketryApplication()),
    )
    await process.add_spiders_to_controller()
    assert len(await process.controller.app.get_all_tasks()) == 1
    asyncio.create_task(process.start(silent=False))
    await process.stop()
    assert total_crawled <= 1, "More than 1 round has been started"
