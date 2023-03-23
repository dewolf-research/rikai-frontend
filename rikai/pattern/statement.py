"""Module defining statements making up pattern."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Set, Tuple

from .operands import Literal, Operand, Variable


class Statement(ABC):
    """Base interface for all statements making up a line in a behavior."""

    @property
    @abstractmethod
    def defines(self) -> Set[Variable]:
        """Return a set of all variables defined by the statement."""

    @property
    @abstractmethod
    def dependencies(self) -> Set[Variable]:
        """Return a set of variables the statement depends on."""

    @property
    @abstractmethod
    def variables(self) -> Set[Variable]:
        """Return a set of all variables referenced in this statement."""
        pass


@dataclass(frozen=True)
class Call(Statement):
    """Class representing a call to an API function."""

    label: str
    parameters: Tuple[Operand, ...]

    def __str__(self):
        """Return a string representation of the call, e.g. foo(x)."""
        return f'{self.label}({", ".join([str(x) for x in self.parameters])})'

    @property
    def defines(self) -> Set[Variable]:
        """Return all variables defined in the call."""
        return set()

    @property
    def dependencies(self) -> Set[Variable]:
        """Return a set of all variables the call depends on."""
        return {x for x in self.parameters if isinstance(x, Variable)}

    @property
    def variables(self) -> Set[Variable]:
        """Return a list of all variables in the call."""
        return self.dependencies


@dataclass(frozen=True)
class Assignment(Statement, ABC):
    """Class representing a statement defining a value."""

    assignee: Variable
    value: Literal | Call

    def __str__(self):
        """Return a string representation, e.g. x = foo(y)."""
        return f"{self.assignee} = {str(self.value)}"

    @property
    def defines(self) -> Set[Variable]:
        """Return all variables defined in the assignment."""
        return {self.assignee}


@dataclass(frozen=True)
class CallAssignment(Assignment):
    """Class assigning the return value fo a call to a variable."""

    value: Call

    @property
    def dependencies(self) -> Set[Variable]:
        """Return a set of all variables the call depends on."""
        return self.value.dependencies

    @property
    def variables(self) -> Set[Variable]:
        """Return a list of all variables in the assignment."""
        return {self.assignee} | self.value.dependencies


@dataclass(frozen=True)
class LiteralAssignment(Assignment):
    """Class assigning a literals value to a variable."""

    value: Literal

    @property
    def dependencies(self) -> Set[Variable]:
        """Return a set of all variables the call depends on."""
        return set()

    @property
    def variables(self) -> Set[Variable]:
        """Return a list of all variables in the assignment."""
        return {self.assignee}
