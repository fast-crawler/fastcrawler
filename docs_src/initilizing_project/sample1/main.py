from docs_src.initilizing_project.sample1.wikipedia import wiki_spider
from fastcrawler import FastCrawler

app = FastCrawler(
    crawlers=wiki_spider,
)
