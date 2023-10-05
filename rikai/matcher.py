"""Module implementing classes dedicated to match pattern on database objects."""
from typing import Tuple

from .data.database import Database
from .data.query import QueryGenerator
from .pattern import Behavior


class PatternMatcher:
    """Class matching pattern on the given database."""

    def __init__(self, db: Database):
        """Create a new instance linked to the given Database object."""
        self._db = db
        self._generator = QueryGenerator()

    def match(self, behavior: Behavior) -> Tuple[Tuple[int, ...], ...]:
        """
        Try to match the given behavior on the database.

        :param behavior: The behavior to be matched.
        :return: A tuple containing tuples with the line numbers of all matches.
        """
        for block in behavior.expand():
            query = self._generator.generate(block)
            result = self._db.query(query)
            if result:
                return tuple(tuple(int(x.as_attribute().get_value()) for x in match.values()) for match in result)
        return tuple()
