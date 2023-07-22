from fastcrawler.engine.aio import AioHttpEngine
from fastcrawler.engine.contracts import EngineProto, Request, Response
from fastcrawler.exceptions import ParserInvalidModelType, ParserValidationError
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
    _is_stopped = False

    def __init__(
        self,
        engine: None | EngineProto = None,
        parser: ParserProtocol | None = None,
        model: BaseModel | None = None,
    ):
        self._engine: EngineProto = engine or AioHttpEngine
        self.parser = parser or HTMLParser
        self.data_model = model or self.data_model
        self._crawled_urls = set()
        self._pending_urls = set()
        self.engine_request_limit = self.engine_request_limit or self._engine.default_request_limit

    @property
    def engine(self) -> EngineProto:
        """Method to access engine"""
        return self._engine

    @property
    def is_stopped(self) -> set:
        """Method to stop spider"""
        return self._is_stopped

    @is_stopped.setter
    def is_stopped(self, value):
        """Method to overwrite stop spider condition"""
        self._is_stopped = value

    @property
    def crawled_urls(self) -> set:
        """Method to access crawled urls"""
        return self._crawled_urls

    @crawled_urls.setter
    def crawled_urls(self, value):
        """Method to overwrite crawled urls"""
        self._crawled_urls = value

    @property
    def pending_urls(self) -> set:
        """Method to access pending urls"""
        return self._pending_urls

    @pending_urls.setter
    def pending_urls(self, value):
        """Method to overwrite pending urls"""
        self._pending_urls = value

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
        """Async Method to initialize the spider"""
        if BaseModel not in self.data_model.__mro__:
            raise ParserInvalidModelType(model=self.data_model)
        for key, obj in vars(self.__class__).items():
            if type(obj) == _Depends:
                inject_func = getattr(
                    getattr(self, key),
                    "inject",
                )
                assert (
                    inject_func is not None
                ), "inject function must be defined"  # TODO: raise custom error
                setattr(
                    self,
                    key,
                    await inject_func(getattr(self, key)),
                )

    async def get_urls(self):
        """Get the urls that are pending to be crawled"""
        result = getattr(self, "pending_urls", None)
        if not result:
            self.pending_urls = (self.start_url or set()).copy()
            self.start_url = set()
        return self.pending_urls

    def update_crawl_urls(self, urls):
        """Add the urls to crawled urls"""
        self.crawled_urls.update(urls)
        return None

    def remove_url_from_crawl_memory(self):
        self.crawled_urls.clear()

    def remove_url_from_pending(self, response: Response):
        """Remove the url from pending urls"""
        self.pending_urls.remove(response.url)
        return None

    def add_url_to_pending(self, urls):
        """Add the urls to pending urls"""
        for url in urls:
            if url not in self.crawled_urls:
                self.pending_urls.add(url)
        return None

    def pass_url_to_current_spider(self, parsing: HTMLParser) -> None:
        """Pass the url to current spider to crawl them again"""
        if hasattr(parsing, "resolver") and parsing.resolver:
            self.add_url_to_pending(parsing.resolver)
        return None

    def pass_url_to_next_spider(self, parsing: HTMLParser) -> None:
        """Pass url to the next spider so that next spider can crawl them"""
        if hasattr(parsing, "next_resolver") and parsing.next_resolver:
            for url in parsing.next_resolver:
                if url not in self.instances[-1].start_url:
                    self.instances[-1].start_url.add(url)
        return None

    def parse(self, data):
        """Parse the data from the response w.t.r data model"""
        parsing: HTMLParser = self.parser(data)
        result = parsing.parse(self.data_model)
        self.pass_url_to_current_spider(parsing)
        self.pass_url_to_next_spider(parsing)
        return result

    async def save(self, all_data: BaseModel) -> None:
        """Save the data to somewhere
        Must be implemented in order to save the data"""
        return None

    def parse_response(self, response: Response):
        """Parse the response from the request"""
        try:
            result = self.parse(response.text)
            return result
        except ParserValidationError as error:
            print(error)
            return None

    async def requests(self, session: EngineProto, requests: list[Request]) -> dict[str, Response]:
        """Send a batch of requests
        Args:
            engine (EngineProto): Engine initaited for sending requests
            requests (list[Request]): list of requests to be sent

        Returns:
            list[Response]: list of responses from the requests
        """
        result: dict[str, Response] = await getattr(session, self.data_model.Config.http_method)(
            requests=requests
        )
        return result

    async def control_condition(self, current_depth) -> bool:
        """Control condition for the crawler to run

        Args:
            current_depth (_type_): the depth of the current crawler

        Returns:
            bool: True if the crawler should continue, False otherwise
        """
        return bool(
            (not self.is_stopped)
            and (current_depth >= self.depth or len(await self.get_urls()) > 0)
        )

    async def run_next_spider(self):
        if hasattr(self, "instances"):
            next_index = self.instances.index(self) + 1
            if len(self.instances) > next_index - 1:
                await self.instances[next_index].start()

    async def start(self, silent: bool = True):
        """Start the crawling process, this method is called by the scheduler.
        Batch by batch, it send requests, process responses and save the results
        """
        try:
            await self.start_up()
            await self.async_init()
            current_depth = 0
            async with self.engine(connection_limit=self.engine_request_limit) as session:
                while await self.control_condition(current_depth):
                    current_depth += 1
                    urls = list(await self.get_urls())
                    for idx in range(0, len(urls), self.engine_request_limit):
                        end_index = idx + self.engine_request_limit
                        batch_urls = urls[idx:end_index]
                        requests = [Request(url=url) for url in batch_urls]
                        responses = await self.requests(session, requests)
                        self.update_crawl_urls(batch_urls)
                        for response in responses.values():
                            self.remove_url_from_pending(response)

                        results = [
                            self.parse_response(response)
                            for response in responses.values()
                            if response
                        ]
                        await self.save(results)
                    self.pending_urls.clear()
            await self._shutdown()
            await self.run_next_spider()
        except Exception as error:
            print(error)
            if not silent:
                raise error from error
        return None

    async def _shutdown(self):
        """Safe Shut down the spider"""
        self.start_url = self.__class__.start_url
        self.remove_url_from_crawl_memory()
        await self.shut_down()
        print("Spider is shuting down ...")

    async def start_up(self):
        """Start up event for the spider"""
        print("Spider is starting up ...")

    async def shut_down(self):
        """Shut down event for spider"""
