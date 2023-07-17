from fastcrawler.engine.aio import AioHttpEngine
from fastcrawler.engine.contracts import EngineProto, Response
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
    data_model: BaseModel
    depth: int = 1_000

    async def async_init(self):
        if type(self.start_url) == _Depends:
            self.start_url = await self.start_url.inject(self.start_url)

    async def get_urls(self):
        result = getattr(self, "pending_urls", None)
        if not result:
            self.pending_urls = (self.start_url or set()).copy()
            self.start_url = set()
        return self.pending_urls

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
        self.engine_request_limit = self.engine_request_limit or engine.default_request_limit

    def __rshift__(self, other: "Spider") -> "Spider":
        """
        leveraged RSHIFT method for magic in flow >>
        clsA >> clsB >> clsC >> clsD

        Must be used as metaclass to inject behaviour to subclass

        DONT TOUCH THIS CLASS UNLESS YOU KNOW WHAT YOU ARE DOING.
        """
        if not getattr(self, "instances", None):
            self.instances = []
            self.instances.append(self)
        self.instances.append(other)
        setattr(other, "instances", self.instances)
        return other

    def parse(self, data):
        parsing: HTMLParser = self.parser(data)
        result = parsing.parse(self.data_model)
        if hasattr(parsing, "resolver") and parsing.resolver:
            for url in parsing.resolver:
                if url not in self.crawled_urls:
                    self.pending_urls.add(url)
        return result

    async def save(self, all_data: list[BaseModel]):
        for data in all_data:
            print(data)

    async def start(self):
        await self.async_init()

        current_depth = 0

        async with self._engine(connection_limit=self.engine_request_limit) as engine:
            while current_depth >= self.depth or len(await self.get_urls()) > 0:
                current_depth += 1
                urls = await self.get_urls()
                responses: list[Response] = await getattr(
                    engine, self.data_model.Config.http_method
                )(urls=urls)
                self.crawled_urls.update(urls)

                # TODO: TRY THIS CODE SNIPET WITH MULTI PROCESSING
                results = []
                for response in responses:
                    if response.status_code == 200:
                        results.append(self.parse(response.text))
                        self.pending_urls.remove(response.url)

                # SAVING METHOD IF NEEDED
                await self.save(results)
