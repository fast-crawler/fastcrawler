from enum import StrEnum

from fastcrawler.engine.contracts import (
    ProxySetting,
    RequestCycle,
    SetCookieParam,
    Response,
    Url,
    Request,
    EngineProto,
)


class Method(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class MockEngine:
    def __init__(
        self,
        cookies: list[SetCookieParam] | None = None,
        headers: dict | None = None,
        user_agent: str | None = None,
        proxy: ProxySetting | None = None,
        connection_limit: int | None = None,
    ):
        super().__init__(cookies, headers, user_agent, proxy, connection_limit)

    async def get(self, requests: list[Request]) -> dict[Url, RequestCycle]:
        """GET HTTP Method for protocol to retrieve a list of URL."""
        return await self.batch(requests, "GET")

    async def post(self, requests: list[Request]) -> dict[Url, RequestCycle]:
        """POST HTTP Method for protocol to crawl a list of URL."""
        return await self.batch(requests, "POST")

    async def put(self, requests: list[Request]) -> dict[Url, RequestCycle]:
        """PUT HTTP Method for protocol to crawl a list of URL."""
        return await self.batch(requests, "PUT")

    async def delete(self, requests: list[Request]) -> dict[Url, RequestCycle]:
        """DELETE HTTP Method for protocol to crawl a list of URL."""
        return await self.batch(requests, "DELETE")


class TestClient:
    def __init__(
        self,
        mapped_routes: dict[tuple[Method, Request], Response],
        mock_engine: EngineProto,
    ) -> None:
        self.mapped_routes = mapped_routes
        self.mock_engine = mock_engine

        self.__default_response = Response(status_code=404)

    def get(self, request: Request):
        return self.mapped_routes.get((Method.GET, request), self.__default_response)


# prepare test

mapped_routes = {
    (Method.GET, Request(url="/user/1")): Response(text=str({"id": 1, "username": "admin"})),
}

mock_engine = MockEngine()  # this just and only just mock the client
mock_client = TestClient(
    mapped_routes, mock_engine
)  # this is high level, for more behavior unsupported to mock the actual server and routing
