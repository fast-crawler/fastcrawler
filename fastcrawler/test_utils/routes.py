from typing import Any
from starlette.routing import NoMatchFound, compile_path

from fastcrawler.test_utils.endpoints import BaseEndpoint


class Route:
    def __init__(
        self,
        request_pattern,
        response: BaseEndpoint,
    ):
        self.request_pattern = request_pattern
        self.response = response
        self.path_regex, self.path_format, self.param_convertors = compile_path(request_pattern)

    def url_path_for(self, url, method: str):
        match = self.path_regex.match(url)
        path_params: dict[str, Any] = {}
        if not match:
            raise NoMatchFound(url, path_params)

        matched_params = match.groupdict()
        for key, value in matched_params.items():
            matched_params[key] = self.param_convertors[key].convert(value)
        path_params.update(matched_params)
        method_func = self.response.dispatch(method.lower())
        return method_func(url, params=path_params)
