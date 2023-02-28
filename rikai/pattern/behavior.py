"""Module defining behavior objects."""
from dataclasses import dataclass
from typing import Dict, Optional, Set, Tuple

from .statement import Assignment, Call, Variable


@dataclass(frozen=True)
class Behavior:
    """Class modelling a potential software behavior-"""

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
        return {assignment.assignee: assignment for assignment in self.assignments}

    def get_definition(self, variable: Variable) -> Optional[Assignment]:
        """Return the definition of the given variable."""
        return self.definitions.get(variable, None)

    def get_dependencies(self, variable: Variable) -> Tuple[Call, ...]:
        """Return the statements dependeing on the given variable."""
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
