"""Class implementing operands utilized in behavior pattern."""
from abc import ABC
from dataclasses import dataclass


class Operand(ABC):
    """Generic base class for all operands."""

    pass


@dataclass(frozen=True)
class Literal(Operand):
    """Base class for string literals."""

    value: str

    def __str__(self):
        """Return the value of the literal."""
        return f'"{self.value}"'


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
