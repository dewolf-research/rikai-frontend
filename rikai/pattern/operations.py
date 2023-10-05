from abc import ABC
from dataclasses import dataclass
from typing import Tuple

from .operands import Operand


@dataclass(frozen=True)
class Operation(Operand, ABC):
    """Base interface for operation constraints."""
    operands: Tuple[Operand, ...]


@dataclass(frozen=True)
class UnaryOperation(Operation, ABC):
    """Base interface for operations with a single operand."""

    @property
    def operand(self) -> Operand:
        return self.operands[0]


@dataclass(frozen=True)
class Compound(Operation):
    """Operand indicating several values have been merged together."""
    SYMBOL = '+'

    def __str__(self):
        return f' {self.SYMBOL} '.join((str(op) for op in self.operands))


@dataclass(frozen=True)
class Branch(UnaryOperation):
    """Operation modeling a conditional branch."""

    def __str__(self):
        return f'if({self.operand})'


class Loop(UnaryOperation):
    """Operation modeling a while loop construct."""

    def __str__(self):
        return f'while({self.operand})'
