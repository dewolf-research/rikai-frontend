"""Module defining the Constraint interface."""
from abc import ABC


class Constraint(ABC):
    """Interface for objects utilized in typedb queries."""

    @property
    def id(self) -> str:
        """Return a unique string identifying the object."""
        return str(id(self))
