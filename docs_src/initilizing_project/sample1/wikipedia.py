# pylint: disable-all


from fastcrawler import BaseModel, Crawler, CSSField, Spider, XPATHField
from fastcrawler.engine import AioHTTP


class PageResolver(BaseModel):
    class Config:
        url_resolver = XPATHField("//a[contains(@href, 'en.wikipedia')]/@href")


class ArticleData(BaseModel):
    title: str = CSSField("h1.firstHeading", extract="text")  # gets text
    body: str = CSSField("div.mw-body-content > div.mw-parser-output")  # gets inner HTML


class WikiBaseSpider(Spider):
    engine = AioHTTP
    concurrency = 100


class WikiArticleFinder(WikiBaseSpider):
    data_model = PageResolver
    req_count = 1_000_000
    start_url = ["https://meta.wikimedia.org/wiki/List_of_Wikipedias", ]


class WikiArticleRetirever(WikiBaseSpider):
    data_model = ArticleData
    req_count = 1_000_000

    async def save_data(self, data: ArticleData): ...  # save parsed data to database


wiki_spider = Crawler(WikiArticleFinder >> WikiArticleRetirever)
