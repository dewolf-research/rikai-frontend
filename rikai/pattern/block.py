from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Generator, Any, Set, Dict, Optional, Iterable

from .statement import Statement, Call, CallAssignment, Reference, Variable, Assignment, Literal
from .constraint import Constraint
from .operations import Condition


@dataclass(frozen=True)
class Block(Constraint):
    """Class modelling a group of statements."""

    statements: Tuple[Statement, ...]

    @property
    def calls(self) -> Generator[Call, Any, None]:
        """Yield all calls contained in the block."""
        for statement in self.statements:
            if isinstance(statement, Call):
                yield statement
            elif isinstance(statement, CallAssignment):
                yield statement.value

    @property
    def references(self) -> Generator[Reference, Any, None]:
        """Iterate all literal references in the block."""
        return (statement for statement in self.statements if isinstance(statement, Reference))

    @property
    def labels(self) -> Set[str]:
        """Return a set of utilized labels."""
        return {x.label for x in self.calls}

    @property
    def variables(self) -> Set[Variable]:
        """Return a set of all variables utilized."""
        return {var for statement in self.statements for var in statement.variables}

    @property
    def literals(self) -> Set[Literal]:
        """Return a set if all literals referenced by the statement."""
        return {literal for statement in self.statements for literal in statement.literals}

    @property
    def assignments(self) -> Tuple[Assignment, ...]:
        """Return all assignment objects contained in the behavior."""
        return tuple(statement for statement in self.statements if isinstance(statement, Assignment))

    @property
    def definitions(self) -> Dict[Variable, Assignment]:
        """Return a dict mapping variables to their assignment statements."""
        return {assignment.assignee: assignment for assignment in self.assignments}

    def get_definition(self, variable: Variable) -> Optional[Assignment]:
        """Return the definition of the given variable."""
        return self.definitions.get(variable, None)

    def get_dependencies(self, variable: Variable) -> Tuple[Statement, ...]:
        """Return the statements depending on the given variable."""
        return tuple(statement for statement in self.statements if variable in statement.dependencies)

    def get_statements(self, label) -> Tuple[Call, ...]:
        """Return all calls referring to the given label."""
        return tuple(call for call in self.calls if call.label == label)

    def get_constraint(self) -> Iterable[str]:
        """Iterate all constraints in the block."""
        for operand in self.literals | self.variables:
            yield from operand.get_constraint()
        for statement in self.statements:
            yield from statement.get_constraint()

    def __str__(self):
        """Return a string representation (reparseable)."""
        return "\n".join([str(x) for x in self.statements])

    def __len__(self):
        """Return the size of the current behavior."""
        return len(self.statements)

    def __iter__(self):
        """iterate all statements in the block."""
        yield from self.statements

    def __add__(self, other: Block) -> Block:
        """Merge two blocks together, generating a new instance."""
        return Block(self.statements + other.statements)


@dataclass(frozen=True)
class Structure(Block):
    """Base class for control flow structures such as branches and loops."""

    condition: Condition

    def get_constraint(self) -> Iterable[str]:
        """Iterate all constraints in the block."""
        yield from super(Structure, self).get_constraint()
        for operand in self.condition.operands:
            for statement in self.statements:
                yield f"({operand.id}, {statement.id}) isa Conditional;"

    @property
    def variables(self) -> Set[Variable]:
        """Return a set of all variables utilized considering the condition."""
        return super(Structure, self).variables | self.condition.variables

    @property
    def literals(self) -> Set[Literal]:
        """Return a set of all literals utilized considering the condition."""
        return super(Structure, self).literals | self.condition.literals

    def __str__(self) -> str:
        """Return a string representation of the structure."""
        return "\n\t".join(["{"] + [str(x) for x in self.statements]) + "\n}"


@dataclass(frozen=True)
class Branch(Structure):
    """Class Modeling a block executed based on a condition to be evaluated."""

    def __str__(self) -> str:
        """Return a string representation of the branch."""
        return f"if ({self.condition})" + super(Branch, self).__str__()


@dataclass(frozen=True)
class Loop(Structure):
    """Class Modeling a block executed in a loop."""

    def __str__(self) -> str:
        """Return a string representation of the loop."""
        return f"while ({self.condition})" + super(Loop, self).__str__()
