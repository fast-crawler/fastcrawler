# pylint: disable=c-extension-no-member
from typing import List

from lxml import etree  # type: ignore[attr-defined]
from lxml import html as lxml_html  # type: ignore[attr-defined]

from .interface import ProcessorInterface


class LxmlProcessor(ProcessorInterface):
    base_element = etree.ElementBase

    @staticmethod
    def to_string(result: etree.ElementBase):
        return lxml_html.tostring(result)

    @staticmethod
    def from_string_by_xpath(string: str, query: str) -> etree.ElementBase:
        tree = lxml_html.fromstring(string)
        results: List[etree.ElementBase] = tree.xpath(query)
        return results

    @staticmethod
    def from_string_by_css(string: str, query: str) -> etree.ElementBase:
        tree = lxml_html.fromstring(string)
        results: List[etree.ElementBase] = tree.cssselect(query)
        return results
