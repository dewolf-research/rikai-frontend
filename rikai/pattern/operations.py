from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Iterable, Set

from . import Literal, Variable
from .operands import Operand


@dataclass(frozen=True)
class Operation(Operand, ABC):
    """Base interface for operation constraints."""

    operands: Tuple[Operand, ...]

    @property
    @abstractmethod
    def SYMBOL(self) -> str:
        """Return an infix symbol for the operation."""
        pass

    @property
    def variables(self) -> Set[Variable]:
        """Return a set of all utilized variables."""
        return {operand for operand in self.operands if isinstance(operand, Variable)}

    @property
    def literals(self) -> Set[Literal]:
        """Return a set of all literals in the operation."""
        return {operand for operand in self.operands if isinstance(operand, Literal)}

    def get_constraint(self) -> Iterable[str]:
        """Yield constraints based on the contained operands."""
        for operand in self.operands:
            yield from operand.get_constraint()

    def __str__(self):
        """Return a string representation of the compound operator."""
        return f' {self.SYMBOL} '.join((str(op) for op in self.operands))


@dataclass(frozen=True)
class Compound(Operation):
    """Operand indicating several values have been merged together."""

    SYMBOL = '+'


class Condition(Operation):
    """Class modelling a condition in a loop or branch."""

    SYMBOL = '|'
