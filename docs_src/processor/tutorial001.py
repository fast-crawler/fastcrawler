import asyncio

from fastcrawler import BaseModel, Depends, Process, Spider, XPATHField
from fastcrawler.schedule import ProcessController, RocketryApplication


class PersonData(BaseModel):
    name: str = XPATHField(query="//td[1]", extract="text")
    age: int = XPATHField(query="//td[2]", extract="text")


class PersonPage(BaseModel):
    person: list[PersonData] = XPATHField(query="//table//tr", many=True)


async def get_urls():
    return {f"http://localhost:8000/persons/{id}" for id in range(20)}


class MySpider(Spider):
    engine_request_limit = 20
    data_model = PersonPage
    start_url = Depends(get_urls)

    async def save(self, all_data: list[PersonPage]):
        assert all_data is not None
        assert len(all_data) == 20


async def main():
    process = Process(
        spider=MySpider(),
        cond="every 1 second",
        controller=ProcessController(app=RocketryApplication()),
    )
    await process.add_spiders_to_controller()
    assert len(await process.controller.app.get_all_tasks()) == 1
    await process.start(silent=False)


asyncio.run(main())
