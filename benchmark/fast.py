import asyncio
import resource
import sys
import time

sys.path.append("../fastcrawler")

from fastcrawler import BaseModel, Crawler, Depends, Spider, XPATHField  # noqa: E402


class PersonData(BaseModel):
    name: str = XPATHField(query="//td[1]", extract="text")
    age: int = XPATHField(query="//td[2]", extract="text")


class PersonPage(BaseModel):
    person: list[PersonData] = XPATHField(query="//table//tr", many=True)


async def get_urls():
    return {f"http://localhost:8000/{id}" for id in range(200)}


class MySpider(Spider):
    engine_request_limit = 20
    data_model = PersonPage
    start_url = Depends(get_urls)

    async def save(self, all_data: PersonPage):
        ...


async def main():
    crawler = Crawler(MySpider())
    await crawler.add_spiders()
    print(await crawler.controller.app.get_all_tasks())
    await crawler.controller.serve()


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    print(f"Time taken: {end_time - start_time} seconds")
    print(f"Memory used: {mem_usage} kilobytes")
