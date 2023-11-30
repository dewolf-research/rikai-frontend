"""Module defining the Constraint interface."""
from abc import ABC, abstractmethod
from typing import Iterable


class Constraint(ABC):
    """Interface for objects utilized in typedb queries."""

    @property
    def id(self) -> str:
        """Return a unique string identifying the object."""
        return f"{self.__class__.__name__}_{id(self)}"

    @abstractmethod
    def get_constraint(self) -> Iterable[str]:
        """Generate TypeDB constraints based on the matchable."""
