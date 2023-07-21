import resource
import time

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings


class MySpider(scrapy.Spider):
    name = "local"
    start_urls = [f"http://localhost:8000/{id}" for id in range(200)]

    def parse(self, response):
        for person in response.css("table tr"):
            yield {
                "name": str(person.css("td:nth-child(1)::text").get()),
                "age": int(person.css("td:nth-child(2)::text").get()),
            }


start_time = time.time()

my_settings = Settings()
my_settings.set("CONCURRENT_REQUESTS", 20)


process = CrawlerProcess(settings=my_settings)
process.crawl(MySpider)
process.start()

end_time = time.time()
mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

print(f"Time taken: {end_time - start_time} seconds")
print(f"Memory used: {mem_usage} kilobytes")
