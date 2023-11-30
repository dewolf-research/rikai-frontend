"""Class implementing operands utilized in behavior pattern."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Set

from .constraint import Constraint


class Operand(Constraint):
    """Generic base class for all operands."""

    @property
    @abstractmethod
    def variables(self) -> Set[Variable]:
        """Return a set of all variables referenced by this operand."""
        pass

    @property
    @abstractmethod
    def literals(self) -> Set[Literal]:
        """Return a set if all literals referenced by this operand."""
        pass


class Literal(Operand, ABC):
    """Base class for all literal types."""

    variables: Set[Variable] = set()

    @property
    def literals(self) -> Set[Literal]:
        """Return a set containing the literal itself."""
        return {self}


@dataclass(frozen=True)
class StringLiteral(Literal):
    """Base class for string literals."""

    value: str

    def __str__(self):
        """Return the string value of the literal."""
        return f'"{self.value}"'

    def get_constraint(self) -> Iterable[str]:
        """Return a constraint on the literal's string value."""
        yield f'{self.id} isa StringLiteral, has StringValue {self.value};'


@dataclass(frozen=True)
class IntegerLiteral(Literal):
    """Base class for string literals."""

    value: int

    def __str__(self):
        """Return the integer value of the literal."""
        return hex(self.value)

    def get_constraint(self) -> Iterable[str]:
        """Return a constraint on the literal's integer value."""
        yield f"{self.id} isa IntegerLiteral, has IntegerValue {self.value};"


@dataclass(frozen=True)
class EnumValue(IntegerLiteral):
    """Class representing a named enum value."""

    name: str

    def __str__(self):
        """Return the name of the enum value."""
        return self.name


@dataclass(frozen=True)
class Variable(Operand):
    """Class representing a bound variable."""

    name: str
    literals = set()

    @property
    def id(self) -> str:
        """Return a variable id based on its name."""
        return f"{self.name}"

    @property
    def variables(self) -> Set[Variable]:
        """Return a set containing """
        return {self}

    def get_constraint(self) -> Iterable[str]:
        yield f"{self.id} isa Variable;"

    def __str__(self):
        """Return the name of the variable."""
        return f"{self.name}"


@dataclass(frozen=True)
class UnboundVariable(Operand):
    """Class representing unbound (don't care) variables."""

    SYMBOL = "_"
    variables = set()
    literals = set()

    def get_constraint(self) -> Iterable[str]:
        """Unbound Variables yield no constraints whatsoever."""
        yield from ()
        return

    def __str__(self):
        """Return the symbol identifying unbound variables."""
        return self.SYMBOL
