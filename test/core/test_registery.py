# pylint: skip-file

import pytest

from fastcrawler import BaseModel, FastCrawler, Process, Spider
from fastcrawler.exceptions import NoCrawlerFoundError


class Nothing(BaseModel):
    ...


def test_crawler_with_task():
    class cls_A(Spider):
        data_model = Nothing

    class cls_B(Spider):
        data_model = Nothing

    class cls_C(Spider):
        data_model = Nothing

    obj1 = cls_A()
    obj2 = cls_B()
    obj3 = cls_C()
    obj = Process(obj1 >> obj2 >> obj3)
    assert [obj1, obj2, obj3] == obj.spider.instances

    client_one = FastCrawler(crawlers=obj)
    client_two = FastCrawler(
        crawlers=[
            obj,
        ]
    )
    assert client_one.crawlers == client_two.crawlers
    with pytest.raises(NoCrawlerFoundError):
        FastCrawler(crawlers=None)
