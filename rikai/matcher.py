"""Module implementing classes dedicated to match pattern on database objects."""
from typing import Tuple

from .data.database import Database
from .data.query import Behavior, QueryGenerator


class PatternMatcher:
    """Class matching pattern on the given database."""

    def __init__(self, db: Database):
        """Create a new instance linked to the given Database object."""
        self._db = db
        self._generator = QueryGenerator

    def match(self, behavior: Behavior) -> Tuple[Tuple[int, ...], ...]:
        """
        Try to match the given behavior on the database.
        :param behavior: The behavior to be matched.
        :return: A tuple containing tuples with the line numbers of all matches.
        """
        query = self._generator.generate(behavior)
        result = self._db.query(query)
        return tuple(tuple(int(x._value) for x in match.values()) for match in result)
