from abc import ABC, abstractmethod

class Middleware(ABC):
    @abstractmethod
    async def process_input(self, *args, **kwargs):
        pass

    @abstractmethod
    async def process_output(self, *args, **kwargs):
        pass

class RequestMiddleware(Middleware):
    @abstractmethod
    async def process_input(self, request):
        pass

    @abstractmethod
    async def process_output(self, response):
        pass
