from fastcrawler import Crawler, FastCrawler

from .imdb import ImdbArticleFinder, ImdbArticleRetirever
from .wikipedia import WikiArticleFinder, WikiArticleRetirever

app = FastCrawler(
    Crawler(ImdbArticleFinder >> ImdbArticleRetirever, cond=...),
    Crawler(WikiArticleFinder >> WikiArticleRetirever, cond=...),
)
app.run()
