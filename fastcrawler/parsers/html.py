from typing import List, Type
from lxml import (
    html as lxml_html,
    etree
)

from pydantic import ValidationError

from fastcrawler.parsers.pydantic import (
    T, BaseModel, URLs, get_inner_model
)
from fastcrawler.parsers.proto import ParserProtocol
from fastcrawler.exceptions import ParserInvalidModelType, ParserValidationError


class XPATHField:
    """
    XPATHField represents a field that can be retrieved from a given HTML
    document using XPath.
    """
    def __init__(self, xpath: str, value: str = None, many: bool = False):
        self.xpath = xpath
        self.value = value
        self.many = many

    def resolve(self, html: str, **_) -> T | List[T] | None:
        """ Resolves HTML input as the xpath value given to list
        """
        tree = lxml_html.fromstring(html)
        results: List[dict] = tree.xpath(self.xpath)
        if self.many:
            if self.value:
                return [
                    (result.get(self.value)) for result in results
                ]
            else:
                results = [
                    (str(result)) if isinstance(
                        result, etree._ElementUnicodeResult
                    )
                    else result
                    for result in results
                ]
                return results

        elif results and self.value:
            return getattr(results[0], self.value)

        else:
            return results[0] if results else None


class XPathList(XPATHField):
    """
    XPathList represents a list of elements that can be retrieved from a given
    HTML document using XPath.

    For example, we have a table that contains many uls.
    so table is actually a list of elements.
    so XPathList must be used to retrieve servals


    Sample Usage:
        class ListItem(BaseModel):
            id: Optional[int] = XPATHField(xpath="//a/@id")
            name: str = XPATHField(xpath="//a", value="text")

        items: List[ListItem] = XPathList(xpath="//ul/li")

    so items look thorugh all //ul/li, fetching their //a as id and name.
    """

    def __init__(self, xpath: str, value: str = None):
        self.value = value
        self.xpath = xpath
        self.many = True

    def resolve(self, html: str, model: object):
        """ Resolves HTML input as the xpath value given
        using lxml library
        recall in recursive so eventually the outer HTML will be sliced to smaller htmls
        """
        results = super().resolve(html)
        results = [
            HTMLParser(lxml_html.tostring(el)).parse(model)
            for el in results
        ]
        return results


class HTMLParser(ParserProtocol):
    """
    HTMLParser parses a given HTML document based on the specified model.
    Using Pydantic model with XpathFIELD and xpahtlist

    Sample Usage:
        html_parser = HTMLParser(html)
        html_parser.parse(a pydantic model)
    """

    def __init__(self, value: str):
        """
        Initiate the HTML file in memory, so it can be parsed later
        as in MULTI PROCESS or etc.
        """
        self.value = value
        self.resolver: URLs = []
        self.data = []

    def parse(self, model: Type[T]) -> T:
        """
        Parse using the pydantic model
        """
        if hasattr(model, "__mro__") and BaseModel in model.__mro__:
            data = {}
            for field_name, field in model.model_fields.items():
                if isinstance(field.default, (XPATHField, XPathList)):
                    data[field_name] = field.default.resolve(
                        html=self.value,
                        model=get_inner_model(model, field_name)
                    )

            if hasattr(model.Config, "url_resolver"):
                model.Config.url_resolver.many = True
                self.resolver = URLs(urls=model.Config.url_resolver.resolve(
                    self.value
                ))

            try:
                self.data: T = model.model_validate(data)
            except ValidationError as error:
                raise ParserValidationError(error.errors())

            return self.data

        else:
            raise ParserInvalidModelType(model=model)
