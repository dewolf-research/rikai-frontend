"""Module defining statements making up pattern."""
from dataclasses import dataclass
from typing import Set, Tuple

from .operands import Operand, Variable


@dataclass(frozen=True)
class Call:
    """Class representing a call to an API function."""

    label: str
    parameters: Tuple[Operand, ...]

    def __str__(self):
        """Return a string representation of the call, e.g. foo(x)."""
        return f'{self.label}({", ".join([str(x) for x in self.parameters])})'

    @property
    def dependencies(self) -> Set[Variable]:
        """Return a set of all variables the call depends on."""
        return {x for x in self.parameters if isinstance(x, Variable)}

    @property
    def variables(self) -> Set[Variable]:
        """Return a list of all variables in the call."""
        return self.dependencies


@dataclass(frozen=True)
class Assignment(Call):
    """Class representing a call returning a value."""

    assignee: Variable

    def __str__(self):
        """Return a string representation, e.g. x = foo(y)."""
        return f"{self.assignee} = {self.label}({', '.join([str(x) for x in self.parameters])})"

    @property
    def variables(self) -> Set[Variable]:
        """Return a set of variables utilized or set in the Assignment."""
        return super().variables | {self.assignee}
