from abc import abstractmethod
from typing import Iterable


class Matchable:
    """Interface class for all parts of a pattern which make up constraints."""

    def id(self) -> int:
        return hash(self)

    @abstractmethod
    def get_constraint(self) -> Iterable[str]:
        """Generate TypeDB constraints based on the matchable."""
