import pytest

from fastcrawler import Depends, Process, Spider
from fastcrawler.schedule import ProcessController, RocketryApplication

from ..shared.core import PersonPage, get_urls

total_crawled = 0


class MySpider(Spider):
    engine_request_limit = 10
    batch_size = 20
    data_model = PersonPage
    start_url = Depends(get_urls)

    async def save(self, all_data: list[PersonPage]):
        assert all_data is not None
        assert len(all_data) == 20
        global total_crawled
        total_crawled += 1


@pytest.mark.asyncio
async def test_process():
    process = Process(
        spider=MySpider(),
        cond="every 1 second",
        controller=ProcessController(app=RocketryApplication()),
    )
    await process.add_spiders()
    assert len(await process.controller.app.get_all_tasks()) == 1
    await process.start(silent=False)
    assert total_crawled == 1, "Not all has been crawled, batching doesn't work fine"
