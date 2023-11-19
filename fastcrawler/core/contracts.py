from abc import ABC, abstractmethod


class ProcessItem(ABC):

    @property
    def instances(self) -> list["ProcessItem"]:
        if not hasattr(self, "_instances"):
            self._instances = [self]
        return self._instances

    def __rshift__(self, other: "ProcessItem") -> "ProcessItem":
        """
        leveraged RSHIFT method for magic in flow >>
        objA >> objB >> objC >> objD
        """
        self.instances.append(other)
        setattr(other, "instances", self.instances)
        return other

    @abstractmethod
    async def start(self):
        ...

