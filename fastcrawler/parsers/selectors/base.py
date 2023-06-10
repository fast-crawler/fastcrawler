from typing import List

from lxml import etree
from lxml import html as lxml_html

from fastcrawler.parsers.pydantic import T


class BaseSelector:
    """Base class for HTML-based selectors that are dependent on lxml family.
    """
    def __init__(
        self,
        query: str,
        extract: str | None = None,
        many: bool = False,
        model: T | None = None
    ):
        self.query = query
        self.extract = extract
        self.many = many
        self.model = model
        self.parser = None

    def __repr__(self):
        """Represents a selector for debugging purposes
        """
        return (
            f"Field(type={self.__class__.__name__} extract={self.extract}, "
            f"many={self.many}, query={self.query})"
        )

    def resolve(self):
        """Must be implemented by outer classes.
        Resolves the selector spefinalized by 'XPATH' or 'CSS' or etc
        """
        raise NotImplementedError("Resolves must be overwritten by subclass")

    def _process_results(self, results: List[etree.ElementBase]) -> T | list[T | None]:
        """Process the results resolved based on the logic
        which is combination of many, and extract.
        """
        if not results:
            return None

        elif self.many:
            results = [
                (self.get_from_exctract(result)) for result in results
            ]
            if self.model:
                results = [
                    self.parser(lxml_html.tostring(el)).parse(self.model)
                    for el in results
                ]
            return results

        else:
            results = self.get_from_exctract(results[0])
            return results

    def get_from_exctract(self, result: etree.ElementBase):
        """
        Resolve the extract from string, to get text from etree.ElementBase
            or to get other attributes or the string of HTML by default
        """
        if self.extract == "text":
            return result.text
        elif self.extract:
            return result.get(self.extract)
        elif not self.many and isinstance(result, etree.ElementBase):
            return lxml_html.tostring(result)
        return result
