# pylint: skip-file

import pytest

from fastcrawler import Crawler, FastCrawler, Spider
from fastcrawler.exceptions import NoCrawlerFoundError


def test_crawler_with_task():
    class cls_A(Spider):
        pass

    class cls_B(Spider):
        pass

    class cls_C(Spider):
        pass

    obj1 = cls_A()
    obj2 = cls_B()
    obj3 = cls_C()
    obj = Crawler(obj1 >> obj2 >> obj3)
    assert [obj1, obj2, obj3] == obj.task.instances

    client_one = FastCrawler(crawlers=obj)
    client_two = FastCrawler(
        crawlers=[
            obj,
        ]
    )
    assert client_one.crawlers == client_two.crawlers
    with pytest.raises(NoCrawlerFoundError):
        FastCrawler(crawlers=None)
