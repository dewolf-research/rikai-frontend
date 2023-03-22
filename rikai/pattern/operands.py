"""Class implementing operands utilized in behavior pattern."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


class Operand(ABC):
    """Generic base class for all operands."""

    pass


class Literal(Operand):
    """Base class for all literal types."""

    pass


@dataclass(frozen=True)
class StringLiteral(Literal):
    """Base class for string literals."""

    value: str

    def __str__(self):
        """Return the string value of the literal."""
        return f'"{self.value}"'


@dataclass(frozen=True)
class IntegerLiteral(Literal):
    """Base class for string literals."""

    value: int

    def __str__(self):
        """Return the integer value of the literal."""
        return hex(self.value)


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

    def __str__(self):
        """Return the name of the variable."""
        return f"{self.name}"


@dataclass(frozen=True)
class UnboundVariable(Operand):
    """Class representing unbound (don't care) variables."""

    SYMBOL = "_"

    def __str__(self):
        """Return the symbol identifying unbound variables."""
        return self.SYMBOL
