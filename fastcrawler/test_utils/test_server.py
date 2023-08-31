from fastcrawler.engine.contracts import Request, Response
from fastcrawler.test_utils.routes import Route, NoMatchFound


class TestServer:
    def __init__(self, routes: list[Route] = None):
        self.routes = routes or []

    def add_route(self, route: Route):
        self.routes.append(route)

    def get_response(self, request: Request) -> Response:
        for route in self.routes:
            try:
                return route.url_path_for(request.url, request.method)
            except NoMatchFound:
                pass
        raise NoMatchFound(request.url, {})
