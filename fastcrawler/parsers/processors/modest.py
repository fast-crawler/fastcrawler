# NOTE: This library is not matured yet to be used


class ModestProcessor:
    @staticmethod
    def to_string(result) -> str:
        """
        Resolves a result to string, by getting the inner html,
        This method is used to iterate over HTML elements to resolve inner pydantic models
        """
        raise NotImplementedError()

    @staticmethod
    def from_string_by_xpath(string: str, query: str):
        """
        Resolves a HTML string by XPATH
        """
        raise NotImplementedError("XPATH is not supported in selectolax")

    @staticmethod
    def from_string_by_css(string: str, query: str):
        """
        Resolves a HTML string by CSS
        """
        raise NotImplementedError("XPATH is not supported in selectolax")
