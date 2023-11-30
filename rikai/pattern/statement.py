"""Module defining statements making up pattern."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Set, Tuple, Iterable

from .constraint import Constraint
from .operands import Literal, Operand, Variable


class Statement(Constraint, ABC):
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

    @property
    @abstractmethod
    def literals(self) -> Set[Literal]:
        """Return a set if all literals referenced by the statement."""
        pass


@dataclass(frozen=True)
class Reference(Statement):
    """Class representing a statement asserting the existence of a given literal."""

    literal: Literal

    variables = set()
    defines = set()
    dependencies = set()

    def get_constraint(self) -> Iterable[str]:
        """Return a constraint based on the contained literal."""
        return self.literal.get_constraint()

    @property
    def literals(self) -> Set[Literal]:
        """Return a set if all literals referenced by the statement."""
        return {self.literal}


@dataclass(frozen=True)
class Call(Statement):
    """Class representing a call to an API function."""

    label: str
    parameters: Tuple[Operand, ...]
    library: str = ""

    def __str__(self):
        """Return a string representation of the call, e.g. foo(x)."""
        return f"{self.library}." if self.library else "" + f'{self.label}({", ".join([str(x) for x in self.parameters])})'

    @property
    def defines(self) -> Set[Variable]:
        """Return all variables defined in the call."""
        return set()

    @property
    def dependencies(self) -> Set[Variable]:
        """Return a set of all variables the call depends on."""
        return set.union(*(param.variables for param in self.parameters))

    @property
    def variables(self) -> Set[Variable]:
        """Return a list of all variables in the call."""
        return self.dependencies

    @property
    def literals(self) -> Set[Literal]:
        """Return all parameters referencing literals."""
        return set.union(*(param.literals for param in self.parameters))

    def _get_typedb_string(self) -> str:
        """Return a typedb declaration for Call Statements."""
        return f'{self.label} isa Call, has Label "{self.label}"'

    def get_constraint(self) -> Iterable[str]:
        """Return TypeDB constraints for this call and its parameters,"""
        yield f'{self.id} isa Call, has Label "{self.label}", has Line $l{id(self)};'
        for i, parameter in enumerate(self.parameters):
            for operand in parameter.literals | parameter.variables:
                yield f"({operand.id}, {self.id}) isa Parameter, has Index {i + 1};"


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

    def get_constraint(self) -> Iterable[str]:
        """Return TypeDB constraints for this assignment,"""
        yield f"({self.id}, {self.assignee.id}) isa Definition;"
        return self.value.get_constraint()


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

    @property
    def literals(self) -> Set[Literal]:
        """Return a set of literals contained in the call."""
        return self.value.literals


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

    @property
    def literals(self) -> Set[Literal]:
        """Return a set of literals contained in the call."""
        return {self.value} | self.value.literals
