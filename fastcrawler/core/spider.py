from typing import List


class SpiderMetaClass(type):
    def __init__(cls,  *args, **kwargs):
        super().__init__(cls)

    def __rshift__(self, other: "Spider") -> "Spider":
        if not getattr(self, "instances", None):
            self.instances = []
            self.instances.append(self)
        self.instances.append(other)
        setattr(other, "instances", self.instances)
        return other


class Spider(metaclass=SpiderMetaClass):
    instances: List["Spider"]
