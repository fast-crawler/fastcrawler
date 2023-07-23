# pylint: disable-all


from fastcrawler import BaseModel, Crawler, CSSField, Spider, XPATHField
from fastcrawler.engine import AioHttpEngine


class PageResolver(BaseModel):
    class Config:
        url_resolver = XPATHField("//a[contains(@href, 'en.Imdbpedia')]/@href")


class ArticleData(BaseModel):
    title: str = CSSField("h1.firstHeading", extract="text")  # gets text
    body: str = CSSField("div.mw-body-content > div.mw-parser-output")  # gets inner HTML


class ImdbBaseSpider(Spider):
    engine = AioHttpEngine
    concurrency = 100


class ImdbArticleFinder(ImdbBaseSpider):
    data_model = PageResolver
    req_count = 1_000_000
    start_url = [
        "https://meta.Imdbmedia.org/Imdb/List_of_Imdbpedias",
    ]


class ImdbArticleRetirever(ImdbBaseSpider):
    data_model = ArticleData
    req_count = 1_000_000

    async def save_data(self, data: ArticleData):
        ...  # save parsed data to database
