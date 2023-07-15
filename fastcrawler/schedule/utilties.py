from rocketry.core import BaseCondition as _BaseCondition


class BaseCondition(_BaseCondition):  # pylint: disable=abstract-method
    """A condition is a thing/occurence that should happen in
    order to something happen.

    Conditions are used to determine whether a task can be started,
    a task should be terminated or the scheduler should shut
    down. Conditions are either true or false.

    A condition could answer for any of the following questions:
        - Current time is as specified (ie. Monday afternoon).
        - A given task has already run.
        - The machine has at least a given amount of RAM.
        - A specific file exists.

    Each condition should have the method ``__bool__`` specified
    as minimum. This method should return ``True`` or ``False``
    depending on whether the condition holds or does not hold.

    Examples
    --------

    Minimum example:

    >>> from rocketry.core import BaseCondition
    >>> class MyCondition(BaseCondition):
    ...     def __bool__(self):
    ...         ... # Code that defines state either
    ...         return True

    Complicated example with parser:

    >>> import os, re
    >>> class IsFooBar(BaseCondition):
    ...     __parsers__ = {
    ...         re.compile(r"is foo '(?P<outcome>.+)'"): "__init__"
    ...     }
    ...
    ...     def __init__(self, outcome):
    ...         self.outcome = outcome
    ...
    ...     def __bool__(self):
    ...         return self.outcome == "bar"
    ...
    ...     def __repr__(self):
    ...         return f"IsFooBar('{self.outcome}')"
    ...
    >>> from rocketry.parse import parse_condition
    >>> parse_condition("is foo 'bar'")
    IsFooBar('bar')
    """
