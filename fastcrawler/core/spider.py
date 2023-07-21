from fastcrawler.engine.aio import AioHttpEngine
from fastcrawler.engine.contracts import EngineProto, Response
from fastcrawler.exceptions import ParserInvalidModelType
from fastcrawler.parsers.contracts import ParserProtocol
from fastcrawler.parsers.html import HTMLParser
from fastcrawler.parsers.schema import BaseModel
from fastcrawler.utils.injection import _Depends


class Spider:
    """
    Spider class to create the actual spider interface
        so that configuration of each spider can be given
        as class properties from the inheritanced class from spider

    instances property hold the instances that were set by metaclass
    that is connected to current spider class
    """

    instances: list["Spider"]
    engine_request_limit: int | None = None
    parser: ParserProtocol
    start_url: set[str] | _Depends
    data_model: BaseModel | None = None
    depth: int = 1_000

    def __init__(
        self,
        engine: None | EngineProto = None,
        parser: ParserProtocol | None = None,
        model: BaseModel | None = None,
    ):
        self._engine: EngineProto = engine or AioHttpEngine
        self.parser = parser or HTMLParser
        self.data_model = model or self.data_model
        self.crawled_urls = set()
        self.pending_urls = set()
        self.engine_request_limit = self.engine_request_limit or self._engine.default_request_limit

    def __rshift__(self, other: "Spider") -> "Spider":
        """
        leveraged RSHIFT method for magic in flow >>
        objA >> objB >> objC >> objD
        """
        if not getattr(self, "instances", None):
            self.instances = []
            self.instances.append(self)
        self.instances.append(other)
        setattr(other, "instances", self.instances)
        return other

    async def async_init(self):
        if type(self.start_url) == _Depends:
            self.start_url = await self.start_url.inject(self.start_url)
        if BaseModel not in self.data_model.__mro__:
            raise ParserInvalidModelType(model=self.data_model)

    async def get_urls(self):
        result = getattr(self, "pending_urls", None)
        if not result:
            self.pending_urls = (self.start_url or set()).copy()
            self.start_url = set()
        return self.pending_urls

    def add_url_to_crawled(self, urls):
        self.crawled_urls.update(urls)
        return None

    def remove_url_from_pending(self, response: Response):
        self.pending_urls.remove(response.url)
        return None

    def add_url_to_pending(self, urls):
        for url in urls:
            if url not in self.crawled_urls:
                self.pending_urls.add(url)
        return None

    def parse(self, data):
        parsing: HTMLParser = self.parser(data)
        result = parsing.parse(self.data_model)
        self.pass_url_to_current(parsing)
        self.pass_url_to_next(parsing)
        return result

    async def save(self, all_data: BaseModel):
        ...

    def pass_url_to_current(self, parsing: HTMLParser) -> None:
        if hasattr(parsing, "resolver") and parsing.resolver:
            self.add_url_to_pending(parsing.resolver)
        return None

    def pass_url_to_next(self, parsing: HTMLParser) -> None:
        if hasattr(parsing, "next_resolver") and parsing.next_resolver:
            for url in parsing.next_resolver:
                if url not in self.instances[-1].start_url:
                    self.instances[-1].start_url.add(url)
        return None

    def process_response(self, response: Response):
        if response.status_code == 200:
            result = self.parse(response.text)
            return result
        return None

    async def control_condition(self, current_depth) -> bool:
        return bool(current_depth >= self.depth or len(await self.get_urls()) > 0)

    async def start(self):
        await self.async_init()
        current_depth = 0

        async with self._engine(connection_limit=self.engine_request_limit) as engine:
            while await self.control_condition(current_depth):
                current_depth += 1
                urls = list(await self.get_urls())
                for idx in range(0, len(urls), self.engine_request_limit):
                    end_index = idx + self.engine_request_limit
                    batch_urls = urls[idx:end_index]
                    responses: list[Response] = await getattr(
                        engine, self.data_model.Config.http_method
                    )(urls=batch_urls)
                    self.add_url_to_crawled(batch_urls)

                    for response in responses:
                        self.remove_url_from_pending(response)

                    results = [self.process_response(response) for response in responses]
                    # SAVING METHOD IF NEEDED
                    await self.save(results)
                self.pending_urls = set()

        return None

    async def start_up(self):
        ...

    async def shut_down(self):
        ...
