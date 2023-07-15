# pylint: disable=c-extension-no-member

from lxml import etree  # type: ignore[attr-defined]
from lxml import html as lxml_html  # type: ignore[attr-defined]


class LxmlProcessor:
    base_element = etree.ElementBase

    @staticmethod
    def to_string(result: etree.ElementBase) -> str:
        """
        Resolves a result to string, by getting the inner html,
        This method is used to iterate over HTML elements to resolve inner pydantic models
        """
        return lxml_html.tostring(result)

    @staticmethod
    def from_string_by_xpath(
        string: str,
        query: str,
    ) -> etree.ElementBase | list[etree.ElementBase] | None:
        """
        Resolves a HTML string by XPATH
        """
        tree = lxml_html.fromstring(string)
        results: list[etree.ElementBase] = tree.xpath(query)
        return results

    @staticmethod
    def from_string_by_css(
        string: str,
        query: str,
    ) -> etree.ElementBase | list[etree.ElementBase] | None:
        """
        Resolves a HTML string by CSS
        """
        tree = lxml_html.fromstring(string)
        results: list[etree.ElementBase] = tree.cssselect(query)
        return results
