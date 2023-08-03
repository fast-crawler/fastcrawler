from fastcrawler import FastCrawler, Process

from .imdb import ImdbArticleFinder, ImdbArticleRetirever
from .wikipedia import WikiArticleFinder, WikiArticleRetirever

app = FastCrawler(
    Process(ImdbArticleFinder >> ImdbArticleRetirever, cond="every 3 minute"),
    Process(WikiArticleFinder >> WikiArticleRetirever, cond="every 3 minute"),
)
app.run()
