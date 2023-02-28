from dataclasses import dataclass
from typing import Set, Tuple

from .operands import Operand, Variable


@dataclass(frozen=True)
class Call:
    label: str
    parameters: Tuple[Operand, ...]

    def __str__(self):
        return f'{self.label}({", ".join([str(x) for x in self.parameters])})'

    @property
    def dependencies(self) -> Set[Variable]:
        return {x for x in self.parameters if isinstance(x, Variable)}

    @property
    def variables(self) -> Set[Variable]:
        return self.dependencies


@dataclass(frozen=True)
class Assignment(Call):
    assignee: Variable

    def __str__(self):
        return f"{self.assignee} = {self.label}({', '.join([str(x) for x in self.parameters])})"

    @property
    def variables(self) -> Set[Variable]:
        return super().variables | {self.assignee}
