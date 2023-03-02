"""Module defining behavior objects."""
from dataclasses import dataclass
from itertools import chain, product
from typing import Any, Dict, Generator, Optional, Set, Tuple

from .statement import Assignment, Call, Variable


@dataclass(frozen=True)
class Block:
    """Class modelling a group of statements."""

    statements: Tuple[Call, ...]

    @property
    def labels(self) -> Set[str]:
        """Return a set of utilized labels."""
        return {x.label for x in self.statements}

    @property
    def variables(self) -> Set[Variable]:
        """Return a set of all variables utilized."""
        return {var for statement in self.statements for var in statement.variables}

    @property
    def assignments(self) -> Tuple[Assignment, ...]:
        """Return all assignment objects contained in the behavior."""
        return tuple(call for call in self.statements if isinstance(call, Assignment))

    @property
    def definitions(self) -> Dict[Variable, Assignment]:
        """Return a dict mapping variables to their assignment statements."""
        return {assignment.assignee: assignment for assignment in self.assignments}

    def get_definition(self, variable: Variable) -> Optional[Assignment]:
        """Return the definition of the given variable."""
        return self.definitions.get(variable, None)

    def get_dependencies(self, variable: Variable) -> Tuple[Call, ...]:
        """Return the statements depending on the given variable."""
        return tuple(call for call in self.statements if variable in call.dependencies)

    def get_statements(self, label):
        """Return all statements referring to the given label."""
        return [x for x in self.statements if x.label == label]

    def __str__(self):
        """Return a string representation (reparseable)."""
        return "\n".join([str(x) for x in self.statements])

    def __len__(self):
        """Return the size of the current behavior."""
        return len(self.statements)


@dataclass(frozen=True)
class Behavior(Block):
    disjunctions: Tuple[Tuple[Block, ...], ...]

    def expand(self) -> Generator[Block, Any, None]:
        """Iterate all possible combinations of statement blocks."""
        for possibility in product(*self.disjunctions):
            yield Block(self.statements + tuple(chain(*(block.statements for block in possibility))))

    @property
    def blocks(self) -> Generator[Block, Any, None]:
        """Iterate all blocks in the behavior."""
        yield Block(self.statements)
        for alternative in self.disjunctions:
            yield from alternative

    @property
    def labels(self) -> Set[str]:
        """Return a set of utilized labels."""
        return set().union(*(block.labels for block in self.blocks))

    @property
    def variables(self) -> Set[Variable]:
        """Return a set of all variables utilized."""
        return set().union(*(block.variables for block in self.blocks))

    def __str__(self):
        """Return a string representation (reparseable)."""
        return "\n".join([str(x) for x in self.statements])

    def __len__(self):
        """Return the size of the current behavior."""
        return len(self.statements)
