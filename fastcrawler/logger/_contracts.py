# pragma: no cover
import logging
from abc import ABC, abstractmethod
from typing import ClassVar, Iterator, Literal, Type, TypeVar

from pydantic.v1 import BaseModel, validator

Item = TypeVar("Item")
Data = TypeVar("Data")

ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0
CRITICAL = 50


class Filterer(ABC):
    """
    A base class for loggers and handlers which allows them to share
    common code.
    """

    def __init__(self):
        """
        Initialize the list of filters to be an empty list.
        """

    def addFilter(self, filter):
        """
        Add the specified filter to this handler.
        """

    def removeFilter(self, filter):
        """
        Remove the specified filter from this handler.
        """

    def filter(self, record):
        """
        Determine if a record is loggable by consulting all the filters.

        The default is to allow the record to be logged; any filter can veto
        this and the record is then dropped. Returns a zero value if a record
        is to be dropped, else non-zero.

        .. versionchanged:: 3.2

           Allow filters to be just callables.
        """


class Handler(Filterer, ABC):

    """
    Handler instances dispatch logging events to specific destinations.

    The base handler class. Acts as a placeholder which defines the Handler
    interface. Handlers can optionally use Formatter instances to format
    records as desired. By default, no formatter is specified; in this case,
    the 'raw' message as determined by record.message is logged.
    """

    def __init__(self, level=NOTSET):
        """
        Initializes the instance - basically setting the formatter to None
        and the filter list to empty.
        """

    def get_name(self):
        """Get name for this logger handler"""

    def set_name(self, name):
        """Set name for this logger handler"""

    name = property(get_name, set_name)

    def createLock(self):
        """
        Acquire a thread lock for serializing access to the underlying I/O.
        """

    def _at_fork_reinit(self):
        """Reinit locks after fork."""

    def acquire(self):
        """
        Acquire the I/O thread lock.
        """

    def release(self):
        """
        Release the I/O thread lock.
        """

    def setLevel(self, level):
        """
        Set the logging level of this handler.  level must be an int or a str.
        """

    def format(self, record):
        """
        Format the specified record.

        If a formatter is set, use it. Otherwise, use the default formatter
        for the module.
        """

    def emit(self, record):
        """
        Do whatever it takes to actually log the specified logging record.

        This version is intended to be implemented by subclasses and so
        """

    def handle(self, record):
        """
        Conditionally emit the specified logging record.

        Emission depends on filters which may have been added to the handler.
        Wrap the actual emission of the record with acquisition/release of
        the I/O thread lock. Returns whether the filter passed the record for
        emission.
        """

    def setFormatter(self, fmt):
        """
        Set the formatter for this handler.
        """
        self.formatter = fmt

    def flush(self):
        """
        Ensure all logging output has been flushed.

        This version does nothing and is intended to be implemented by
        subclasses.
        """

    def close(self):
        """
        Tidy up any resources used by the handler.

        This version removes the handler from an internal map of handlers,
        _handlers, which is used for handler lookup by name. Subclasses
        should ensure that this gets called from overridden close()
        methods.
        """
        # get the module data lock, as we're updating a shared structure.

    def handleError(self, record):
        """
        Handle errors which occur during an emit() call.

        This method should be called from handlers when an exception is
        encountered during an emit() call. If raiseExceptions is false,
        exceptions get silently ignored. This is what is mostly wanted
        for a logging system - most users will not care about errors in
        the logging system, they are more interested in application errors.
        You could, however, replace this with a custom handler if you wish.
        The record which was being processed is passed in to this method.
        """


class RepoHandler(Handler, ABC):
    """Log handler that writes log records to a repository

    Useful for cases where the log records need to be read
    programmatically.

    Parameters
    ----------
    repo : BaseRepo
        Repository where the log records are written
    **kwargs : dict
        Keyword arguments passed to logging.Handler
        init
    """

    @abstractmethod
    def __init__(self, repo: "BaseRepo", **kwargs):
        """Initialize the handler"""

    @abstractmethod
    def emit(self, record: logging.LogRecord):
        "Log the log record"

    @abstractmethod
    def write(self, record: dict):
        "Write a log record to the repository"


class BaseResult(ABC):
    """Abstract filter result

    Result classes add additional alchemy
    to Red Bird providing convenient ways
    to read, modify or delete data.

    Subclass of BaseRepo should also have custom
    subclass of BaseResult as cls_result attribute.
    """

    query_: dict
    repo: "BaseRepo"

    def __init__(self, query: dict = None, repo: "BaseRepo" = None):
        """Initilize Result of a query"""

    def first(self) -> Item:
        "Return first item"

    def last(self) -> Item:
        "Return last item"

    def all(self) -> list[Item]:
        "Return all items"

    def limit(self, n: int) -> list[Item]:
        "Return n items"

    def query(self) -> Iterator[Item]:
        "Get actual result"

    @abstractmethod
    def query_data(self) -> Iterator[Data]:
        "Get actual result"

    def __iter__(self) -> Iterator[Item]:
        """iterator for the result"""

    @abstractmethod
    def update(self, **kwargs):
        "Update the resulted items"

    @abstractmethod
    def delete(self):
        "Delete the resulted items"

    def replace(self, __values: dict = None, **kwargs):
        "Replace the existing item(s) with given"
        if __values is not None:
            kwargs.update(__values)
        if self.count() > 1:
            raise KeyError("You may only replace one item.")
        self.delete()
        self.repo.add(kwargs)

    def count(self) -> int:
        "Count the resulted items"
        return len(list(self))

    def format_query(self, query: dict) -> dict:
        "Turn the query to a form that's understandable by the underlying database"
        qry = self.repo.query_model(**query)
        return qry.format(self.repo) if hasattr(qry, "format") else qry.dict()


class BaseRepo(ABC, BaseModel):
    """Abstract Repository

    Base class for the repository pattern.

    Parameters
    ----------
    model : Type
        Class of an item in the repository.
        Commonly dict or subclass of Pydantic
        BaseModel. By default dict
    id_field : str, optional
        Attribute or key that identifies each item
        in the repository.
    field_access : {'attr', 'key'}, optional
        How to access a field in an item. Either
        by attribute ('attr') or key ('item').
        By default guessed from the model.
    query : Type, optional
        Query model of the repository.
    errors_query : {'raise', 'warn', 'discard'}
        Whether to raise an exception, warn or discard
        the item in case of validation error in
        converting data to the item model from
        the repository. By default raise
    """

    cls_result: ClassVar[Type[BaseResult]]

    model: dict
    id_field: str | None
    query_model: Type[BaseModel] | None
    errors_query: Literal["raise", "warn", "discard"] = "raise"
    field_access: Literal["attr", "key", "infer"] = "infer"

    # Attributes that specifies how the repo behaves
    ordered: bool

    @validator("id_field", always=True)
    def set_id_field(cls, value, values):
        """Set id_field if not set"""

    def __iter__(self) -> Iterator[Item]:
        "Iterate over the repository"

    def __getitem__(self, id) -> Item:
        "Get item from the repository using ID"

    def __delitem__(self, id):
        "Delete item from the repository using ID"

    def __setitem__(self, id, attrs: dict):
        "Update given item"

    # Item based
    def add(self, item: Item, if_exists="raise"):
        "Add an item to the repository"

    @abstractmethod
    def insert(self):
        """Insert item to the repository

        Parameters
        ----------
        item: instance of model
            Item to insert to the repository

        Examples
        --------
        .. code-block:: python

            repo.insert(Item(id="a", color="red"))
        """

    def upsert(self, item: Item):
        """Upsert item to the repository

        Upsert is an insert if the item
        does not exist in the repository
        and update if it does.

        Parameters
        ----------
        item: instance of model
            Item to upsert to the repository

        Examples
        --------
        .. code-block:: python

            repo.upsert(Item(id="a", color="red"))
        """

    def delete(self, item: Item):
        """Delete item from the repository

        Parameters
        ----------
        item: instance of model
            Item to delete from the repository

        Examples
        --------
        .. code-block:: python

            repo.delete(Item(id="a", color="red"))
        """

    def update(self, item: Item):
        """Update item in the repository

        Parameters
        ----------
        item: instance of model
            Item to update in the repository

        Examples
        --------
        .. code-block:: python

            repo.update(Item(id="a", color="red"))
        """

    def replace(self, item: Item):
        "Update an item in the repository"

    def item_to_dict(self, item: Item, exclude_unset=True) -> dict:
        """Convert item to dict"""

    def get_by(self, id):
        "Get item based on ID but returns result for further operations"

    def filter_by(self, **kwargs) -> BaseResult:
        """Filter the repository

        Parameters
        ----------
        **kwargs : dict
            Query which is used to conduct
            furher operation.

        Examples
        --------
        .. code-block:: python

            repo.filter_by(color="red")
        """

    def data_to_item(self, data: Data) -> Item:
        "Turn object from repo (row, doc, dict, etc.) to item"

    def to_item(self, obj) -> Item:
        "Turn an object to item"

    def get_field_value(self, item: Item, key):
        """Utility method to get key's value from an item

        If item's fields are accessed via attribute,
        getattr is used. If fields are accessed via
        items, getitem is used.
        """

    def set_field_value(self, item: Item, key, value):
        """Utility method to set field's value in an item

        If item's fields are accessed via attribute,
        setattr is used. If fields are accessed via
        items, setitem is used.
        """


class TemplateResult(BaseResult, ABC):
    repo: "TemplateRepo"

    def query(self) -> Iterator[Item]:
        "Get actual result"

    def query_data(self) -> Iterator[Data]:
        "Get actual result"

    def update(self, **kwargs):
        """Update the result of the query with given values"""

    def delete(self):
        """Delete the result of the query""" ""

    def replace(self, __values: dict = None, **kwargs):
        "Replace the existing item(s) with given"

    def count(self) -> int:
        """Count the items returned by the query"""

    def first(self) -> Item:
        """Query the first item"""

    def limit(self, n: int) -> list[Item]:
        """Query the first n items"""

    def last(self) -> Item:
        """Query the last item""" ""

    def format_query(self, query: dict) -> dict:
        """Format the query to a format suitable by the repository"""


class TemplateRepo(BaseRepo, ABC):
    """Template repository for easy subclassing

    Parameters
    ----------
    model : Type
        Class of an item in the repository.
        Commonly dict or subclass of Pydantic
        BaseModel. By default dict
    id_field : str, optional
        Attribute or key that identifies each item
        in the repository.
    field_access : {'attr', 'key'}, optional
        How to access a field in an item. Either
        by attribute ('attr') or key ('item').
        By default guessed from the model.
    query : Type, optional
        Query model of the repository.
    errors_query : {'raise', 'warn', 'discard'}
        Whether to raise an exception, warn or discard
        the item inn case of validation error in
        converting data to the item model from
        the repository. By default raise

    Examples
    --------

    .. code-block:: python

        class MyRepo(TemplateRepo):

            def insert(self, item):
                # Insert item to the data store
                ...

            def query_read(self, query: dict):
                # Get data from repository
                for item in ...:
                    yield item

            def query_update(self, query: dict, values: dict):
                # Update items with values matcing the query
                ...

            def query_delete(self, query: dict):
                # Delete items matcing the query
                ...

            def item_to_data(self, item):
                # Convert item to type that is understandable
                # by the repository's data store
                ...
                return data
    """

    cls_result: ClassVar = TemplateResult

    @abstractmethod
    def query_data(self, query: dict) -> Iterator[Data]:
        """Query (read) the data store and return raw data

        Override this or :func:`~redbird.templates.TemplateRepo.query_items` method.

        Parameters
        ----------
        query : dict
            Repository query, by default dict.

        Returns
        -------
        iterable (any)
            Iterable of raw data that is converted to an item using :func:`~redbird.base.BaseRepo
            data_to_item`

        Examples
        --------

        Used in following cases:

        .. code-block:: python

            repo.filter_by(color="red").all()

        """

    @abstractmethod
    def query_items(self, query: dict) -> Iterator[Item]:
        """Query (read) the data store and return items

        Override this or :func:`~redbird.templates.TemplateRepo.query_data` method.

        Parameters
        ----------
        query : dict
            Repository query, by default dict.

        Returns
        -------
        iterable (``model``)
            Items that are instances of the class in the ``model`` attibute.
            Typically dicts or instances of subclassed Pydantic BaseModel

        Examples
        --------

        Used in following cases:

        .. code-block:: python

            repo.filter_by(color="red").all()

        """

    @abstractmethod
    def query_update(self, query: dict, values: dict):
        """Update the result of the query with given values

        Override this method.

        Parameters
        ----------
        query : any
            Repository query, by default dict.

        Examples
        --------

        Used in following cases:

        .. code-block:: python

            repo.filter_by(color="red").update(color="blue")

        """
        ...

    @abstractmethod
    def query_delete(self, query: dict):
        """Delete the result of the query

        Override this method.

        Parameters
        ----------
        query : any
            Repository query, by default dict.

        Examples
        --------

        Used in following cases:

        .. code-block:: python

            repo.filter_by(color="red").delete()

        """

    @abstractmethod
    def query_read_first(self, query: dict) -> Item:
        """Query the first item

        You may override this method. By default,
        the first item returned by :class:`TemplateRepo.query_read`
        is returned.

        Parameters
        ----------
        query : any
            Repository query, by default dict.

        Examples
        --------

        Used in the following case:

        .. code-block:: python

            repo.filter_by(color="red").first()

        """

    @abstractmethod
    def query_read_limit(self, query: dict, n: int) -> list[Item]:
        """Query the first n items

        You may override this method. By default,
        the N first items returned by :class:`TemplateRepo.query_read`
        are returned.

        Parameters
        ----------
        query : any
            Repository query, by default dict.
        n : int
            Number of items to return

        Examples
        --------

        Used in the following case:

        .. code-block:: python

            repo.filter_by(color="red").limit(3)

        """

    @abstractmethod
    def query_read_last(self, query: dict) -> Item:
        """Query the last item

        You may override this method. By default,
        the last item returned by :class:`TemplateRepo.query_read`
        is returned.

        Parameters
        ----------
        query : any
            Repository query, by default dict.

        Examples
        --------

        Used in the following case:

        .. code-block:: python

            repo.filter_by(color="red").last()

        """

    @abstractmethod
    def query_replace(self, query: dict, values: dict):
        """Replace the items with given values using given query

        You may override this method. By default,
        the result of the query is deleted and an
        item from the values is generated.

        Parameters
        ----------
        query : any
            Repository query, by default dict.
        values : dict
            Values to replace the items' existing
            values with

        Examples
        --------

        Used in the following case:

        .. code-block:: python

            repo.filter_by(color="red").replace(color="blue")

        """

    @abstractmethod
    def query_count(self, query: dict):
        """Count the items returned by the query

        You may override this method. By default,
        the items returned by :class:`TemplateRepo.query_read`
        are counted.

        Parameters
        ----------
        query : any
            Repository query, by default dict.

        Examples
        --------

        Used in the following case:

        .. code-block:: python

            repo.filter_by(color="red").count()

        """

    @abstractmethod
    def format_query(self, query: dict) -> dict:
        """Format the query to a format suitable by the repository

        You may override this method. By default,
        the query is as dictionary.

        Parameters
        ----------
        query : dict
            Query to reformat

        Examples
        --------

        Used in the following case:

        .. code-block:: python

            repo.filter_by(color="red")

        """


Repo = TypeVar("Repo", bound=TemplateRepo)
BaseRepoHandler = TypeVar("BaseRepoHandler", bound=RepoHandler)
