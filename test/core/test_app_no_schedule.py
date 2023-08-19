import pytest

from fastcrawler import Depends, FastCrawler, Process, Spider

from ..shared.core import PersonPage, get_urls

total_crawled = 0


class MySpider(Spider):
    engine_request_limit = 10
    batch_size = 10
    data_model = PersonPage
    start_url = Depends(get_urls)

    async def save(self, all_data: list[PersonPage]):
        assert all_data is not None
        assert len(all_data) == 10
        global total_crawled
        total_crawled += 1


@pytest.mark.asyncio
async def test_process():
    app = FastCrawler(
        crawlers=Process(
            spider=MySpider(),
            cond="every 1 second",
        )
    )
    await app.startup()
    await app._shutdown()
    await app.start()
    assert total_crawled == 2, "Not all has been crawled"
    assert len(app.get_all_serves) == 1, "Where is controller serve?"
