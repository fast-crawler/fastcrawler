import asyncio
from typing import Any, Self, Type

from fastcrawler.engine.aio import AioHttpEngine
from fastcrawler.engine.contracts import EngineProto, Request, RequestCycle
from fastcrawler.exceptions import (
    ParserInvalidModelType,
    ParserValidationError,
    SpiderBadConfiguratonError,
)
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

    engine_request_limit: int | None = None
    parser: Type[ParserProtocol] | None
    start_url: set[str] | _Depends
    data_model: Type[BaseModel] | None = None
    max_depth: int | None = None
    _is_stopped = False
    batch_size: int | None = None
    request_sleep_interval: float | None = None
    cycle_sleep_interval: float | None = None
    max_request_count: int | None = None

    def __init__(
        self,
        engine: None | Type[EngineProto] = None,
        parser: Type[ParserProtocol] | None = None,
        model: Type[BaseModel] | None = None,
    ):
        self._engine: Type[EngineProto] = engine or AioHttpEngine  # type: ignore

        if model is None and self.data_model is None:
            raise SpiderBadConfiguratonError("A data model must be specified")

        if self.engine_request_limit is None and self._engine.default_request_limit is None:
            raise SpiderBadConfiguratonError("Request limit must be specified")

        self.parser = parser or HTMLParser
        self._data_model: Type[BaseModel] = model or self.data_model  # type: ignore
        self._crawled_urls = set()
        self._pending_urls = set()
        self._engine_request_limit: int = (
            self.engine_request_limit or self._engine.default_request_limit
        )
        self.request_sent = 0

    @property
    def engine(self) -> Type[EngineProto]:
        """Method to access engine"""
        return self._engine

    @property
    def instances(self) -> list[Self | "Spider"]:
        if not hasattr(self, "_instances"):
            self._instances = [self]
        return self._instances

    @instances.setter
    def instances(self, value: list["Spider"]):
        self._instances = value

    @property
    def is_stopped(self) -> bool:
        """Method to stop spider"""
        return self._is_stopped

    @is_stopped.setter
    def is_stopped(self, value: bool):
        """Method to overwrite stop spider condition"""
        self._is_stopped = value

    @property
    def crawled_urls(self) -> set[str]:
        """Method to access crawled urls"""
        return self._crawled_urls

    @crawled_urls.setter
    def crawled_urls(self, value):
        """Method to overwrite crawled urls"""
        self._crawled_urls = value

    @property
    def pending_urls(self) -> set[str]:
        """Method to access pending urls"""
        return self._pending_urls

    @pending_urls.setter
    def pending_urls(self, value):
        """Method to overwrite pending urls"""
        self._pending_urls = value

    @property
    def get_batch_size(self) -> int:
        if self.batch_size:
            return self.batch_size
        elif self._engine_request_limit:
            return self._engine_request_limit * 2
        raise SpiderBadConfiguratonError(
            "batch size and engine_request_limit is not initialized"
            ", please make sure one is initialized"
        )

    def __rshift__(self, other: "Spider") -> "Spider":
        """
        leveraged RSHIFT method for magic in flow >>
        objA >> objB >> objC >> objD
        """
        self.instances.append(other)
        setattr(other, "instances", self.instances)
        return other

    async def async_init(self) -> None:
        """Async Method to initialize the spider"""
        if BaseModel not in self._data_model.__mro__:
            raise ParserInvalidModelType(model=self._data_model)
        for key, obj in vars(self.__class__).items():
            if type(obj) == _Depends:
                inject_func = getattr(getattr(self, key), "inject", None)
                if inject_func is None:
                    raise SpiderBadConfiguratonError(
                        "Depends on the class variable is not correctly defined"
                    )

                setattr(self, key, await inject_func(getattr(self, key)))
        return None

    async def get_urls(self) -> set[str]:
        """Get the urls that are pending to be crawled"""
        result = getattr(self, "pending_urls", None)
        if not result:
            assert type(self.start_url) is set
            self.pending_urls = (self.start_url or set()).copy()
            self.start_url = set()
        return self.pending_urls

    def update_crawl_urls(self, urls) -> None:
        """Add the urls to crawled urls"""
        self.crawled_urls.update(urls)
        return None

    def remove_url_from_crawl_memory(self) -> None:
        self.crawled_urls.clear()

    def remove_url_from_pending(self, response: RequestCycle) -> None:
        """Remove the url from pending urls"""
        self.pending_urls.remove(str(response.response.url))
        return None

    def add_url_to_pending(self, urls: set[str]) -> None:
        """Add the urls to pending urls"""
        for url in urls:
            if url not in self.crawled_urls:
                self.pending_urls.add(url)
        return None

    def pass_url_to_current_spider(self, urls: set[str]) -> None:
        """Pass the url to current spider to crawl them again"""
        self.add_url_to_pending(urls)
        return None

    def pass_url_to_next_spider(self, urls) -> None:
        """Pass url to the next spider so that next spider can crawl them"""
        for url in urls:
            assert type(self.instances[-1].start_url) is set
            if url not in self.instances[-1].start_url:
                self.instances[-1].start_url.add(str(url))
        return None

    def parse(self, data: str) -> BaseModel | None:
        """Parse the data from the response w.t.r data model"""
        if self.parser and self._data_model:
            parsing: HTMLParser = self.parser(data)  # type: ignore
            # TODO: investigate why HTMLParser doesn't respect proto
            result = parsing.parse(self._data_model)

            # TODO: handle logic for passing url to next/current spider
            if hasattr(parsing, "resolver") and parsing.resolver:
                self.pass_url_to_current_spider(parsing.resolver)  # type: ignore
                # TODO: use string, not URL

            if hasattr(parsing, "next_resolver") and parsing.next_resolver:
                self.pass_url_to_next_spider(parsing.next_resolver)
            return result

        return None

    async def save(self, all_data: list[Any | BaseModel | None]) -> None:
        """
        Save the data to somewhere
        Must be implemented in order to save the data
        """
        return None

    async def save_cycle(self, all_data: list[RequestCycle]) -> None:
        """
        Save the flow of request (request cycle)
        Must be overwritten if you wish to save more than just the parsed data
        """
        await self.save([data.parsed_data for data in all_data if data and data.parsed_data])
        return None

    def parse_response(self, response: RequestCycle) -> RequestCycle:
        """Parse the response from the request"""
        try:
            if response.response.text:
                response.parsed_data = self.parse(response.response.text)
        except ParserValidationError as error:
            print(error)
            # TODO: handle with error handler
        return response

    async def requests(
        self, session: EngineProto, requests: list[Request]
    ) -> dict[str, RequestCycle]:
        """Send a batch of requests
        Args:
            engine (EngineProto): Engine initiated for sending requests
            requests (list[Request]): list of requests to be sent

        Returns:
            list[Response]: list of responses from the requests
        """
        result: dict[str, RequestCycle] = await getattr(
            session, self._data_model.Config.http_method
        )(requests=requests)
        if result:
            self.request_sent += 1
        return result

    async def control_condition(self, current_depth) -> bool:
        """Control condition for the crawler to run

        Args:
            current_depth (_type_): the depth of the current crawler

        Returns:
            bool: True if the crawler should continue, False otherwise
        """
        if self.is_stopped:
            return False

        elif isinstance(self.max_depth, int) and current_depth >= self.max_depth:
            return False

        elif (
            isinstance(self.max_request_count, int) and self.request_sent >= self.max_request_count
        ):
            # BUG: we may send more request sent than max_request_count in middle of batch
            # because this check is not done after each request, but before each batch

            # TODO: Fix the above bug.
            return False

        else:
            return len(await self.get_urls()) > 0

    async def run_spider_from_instances(self, index: int) -> None:
        """Method to call next spider, if it exists"""
        await self.instances[index].start()
        return None

    async def start(self, silent: bool = True) -> None:
        """Start the crawling process, this method is called by the scheduler.
        Batch by batch, it send requests, process responses and save the results
        """
        try:
            await self.start_up()
            await self.async_init()
            current_depth = 0
            async with self.engine(connection_limit=self._engine_request_limit) as session:
                while await self.control_condition(current_depth):
                    urls = list(await self.get_urls())
                    for idx in range(0, len(urls), self.get_batch_size):
                        if await self.control_condition(current_depth):
                            current_depth += 1
                            end_index = idx + self.get_batch_size
                            batch_urls = urls[idx:end_index]
                            requests = [
                                Request(url=url, sleep_interval=self.request_sleep_interval)
                                for url in batch_urls
                            ]
                            responses = await self.requests(session, requests)
                            self.update_crawl_urls(batch_urls)
                            for response in responses.values():
                                self.remove_url_from_pending(response)

                            results = [
                                self.parse_response(response)
                                for response in responses.values()
                                if response
                            ]
                            await self.save_cycle(results)
                    self.pending_urls.clear()
                    if self.cycle_sleep_interval:
                        await asyncio.sleep(self.cycle_sleep_interval)
            await self._shutdown()
            if hasattr(self, "instances"):
                next_index = self.instances.index(self) + 1
                if len(self.instances) > next_index:
                    await self.run_spider_from_instances(index=next_index)

        except Exception as error:
            print(error)
            if not silent:
                raise error from error
        return None

    async def _shutdown(self) -> None:
        """Safe Shut down the spider"""
        self.start_url = self.__class__.start_url
        self.remove_url_from_crawl_memory()
        await self.shut_down()
        print("Spider is shuting down ...")
        return None

    async def start_up(self) -> None:
        """Start up event for the spider"""
        print("Spider is starting up ...")
        return None

    async def shut_down(self) -> None:
        """Shut down event for spider"""
        return None
