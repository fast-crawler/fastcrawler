<p align="center">
  <a href="https://github.com/fast-crawler/"><img src="https://avatars.githubusercontent.com/u/134741061?s=200&v=4" alt="FastCrawler"></a>
</p>
<p align="center">
    <em>FastCrawler framework, high performance, easy to learn, fast to code, ready for production</em>
</p>
<p align="center">
<a href="https://github.com/tiangolo/fastapi/actions?query=workflow%3ATest+event%3Apush+branch%3Amaster" target="_blank">
    <img src="https://github.com/tiangolo/fastapi/workflows/Test/badge.svg?event=push&branch=master" alt="Test">
</a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/tiangolo/fastapi" target="_blank">
    <img src="https://coverage-badge.samuelcolvin.workers.dev/tiangolo/fastapi.svg" alt="Coverage">
</a>
<a href="https://pypi.org/project/fastapi" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/fastapi" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fastapi.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Documentation**: <a href="https://github.com/fast-crawler/" target="_blank">https://github.com/fast-crawler/</a>

**Source Code**: <a href="https://github.com/fast-crawler/" target="_blank">https://github.com/fast-crawler/</a>

---

FastCrawler is a modern, fast (high-performance), web crawling framework for building Scrapers with Python 3.11+ based on standard Python type hints.

The key features are:

* **Fast**: Very high performance, on par with **NodeJS** and **Go** (thanks to Starlette and Pydantic). [One of the fastest Python frameworks available](#performance).
* **Fast to code**: Increase the speed to develop features by about 200% to 300%. *
* **Fewer bugs**: Reduce about 40% of human (developer) induced errors. *
* **Intuitive**: Great editor support. <abbr title="also known as auto-complete, autocompletion, IntelliSense">Completion</abbr> everywhere. Less time debugging.
* **Easy**: Designed to be easy to use and learn. Less time reading docs.
* **Short**: Minimize code duplication. Multiple features from each parameter declaration. Fewer bugs.
* **Robust**: Get production-ready code. With automatic interactive documentation.
* **Standards-based**: Based on (and fully compatible with) the open standards for APIs: <a href="https://github.com/OAI/OpenAPI-Specification" class="external-link" target="_blank">OpenAPI</a> (previously known as Swagger) and <a href="https://json-schema.org/" class="external-link" target="_blank">JSON Schema</a>.

<small>* estimation based on tests on an internal development team, building production applications.</small>

<!-- ## Sponsors -->

<!-- sponsors -->

<!-- {% if sponsors %}
{% for sponsor in sponsors.gold -%}
<a href="{{ sponsor.url }}" target="_blank" title="{{ sponsor.title }}"><img src="{{ sponsor.img }}" style="border-radius:15px"></a>
{% endfor -%}
{%- for sponsor in sponsors.silver -%}
<a href="{{ sponsor.url }}" target="_blank" title="{{ sponsor.title }}"><img src="{{ sponsor.img }}" style="border-radius:15px"></a>
{% endfor %}
{% endif %} -->

<!-- /sponsors -->

<!-- <a href="https://fastapi.tiangolo.com/fastapi-people/#sponsors" class="external-link" target="_blank">Other sponsors</a> -->


## Requirements

Python 3.11+

FastCrawler stands on the shoulders of giants:

* <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a> for the data parts.

## Installation

<div class="termy">

```console
$ pip install fastcrawler

---> 100%
```

</div>



## Example

### Create it

* Create a file `main.py` with:

```Python
from fastcrawler import Spider, Crawler, Parser

class CategoryUrlParser(Parser):
    class Config:
        urls_resolver = parser.JsonField("category.url")

class ProductParser(Parser):
    name: str = parser.JsonField("product.name")
    price: int = parser.JsonField("product.price")

class DigikalaList(Spider):
    url = "https://google.com"
    parser = CategoryUrlParser

Crawler(
    DigikalaList >> DigikalaDetail
)
```


### Run it

Run the server with:


```console
$ python main.py
```


## License

This project is licensed under the terms of the MIT license.
