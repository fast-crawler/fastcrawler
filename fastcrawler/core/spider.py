from typing import List


class SpiderMetaClass(type):
    def __rshift__(self, other: "Spider") -> "Spider":
        """
        leveraged RSHIFT method for magic in flow >>
        objA >> objB >> objC >> objD

        Must be used as metaclass to inject behaviour to subclass

        DONT TOUCH THIS CLASS UNLESS YOU KNOW WHAT YOU ARE DOING.
        """
        if not getattr(self, "instances", None):
            self.instances = []
            self.instances.append(self)
        self.instances.append(other)
        setattr(other, "instances", self.instances)
        return other


class Spider(metaclass=SpiderMetaClass):
    """
    Spider class to create the actual spider interface
        so that configuration of each spider can be given
        as class properties from the inheritanced class from spider

    instances property hold the instances that were set by metaclass
    that is connected to current spider class
    """

    instances: List["Spider"]
