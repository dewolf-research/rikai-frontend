"""Module defining behavior objects."""
from __future__ import annotations
from dataclasses import dataclass
from itertools import chain, product
from typing import Any, Dict, Generator, Set, Tuple, Iterable

from .block import Block
from .operands import Variable


@dataclass(frozen=True)
class Disjunction:
    """Class modelling a block with several alternatives."""

    value: str
    possibilities: Dict[str, Block]

    @property
    def blocks(self) -> Tuple[Block, ...]:
        """Return all Blocks in the disjunction."""
        return tuple(self.possibilities.values())

    def __str__(self) -> str:
        """Return a string representation of the disjunction with its blocks and their names."""
        return f"switch({self.value}) {{\n" + "\n".join(
            f"\tcase {name}:\n\t\t" + "\n\t\t".join(str(block).splitlines() + ["break"]) for name, block in self.possibilities.items()
        ) + "\n}"


@dataclass(frozen=True)
class Behavior:
    """Class modelling a behavior, potentially containing several blocks."""

    blocks: Tuple[Block, ...]
    disjunctions: Tuple[Disjunction, ...]

    @property
    def labels(self) -> Set[str]:
        """Return a set of utilized labels."""
        return set().union(*(block.labels for block in self.blocks))

    @property
    def variables(self) -> Set[Variable]:
        """Return a set of all variables utilized."""
        return set().union(*(block.variables for block in self.blocks))

    def expand(self) -> Iterable[Behavior]:
        """Iterate all possible combinations of statement blocks."""
        for possibility in product(tuple(disjunction.possibilities.values()) for disjunction in self.disjunctions):
            yield Behavior(self.blocks + possibility, tuple())

    def get_constraint(self) -> Iterable[str]:
        """Iterate all constraints in the pattern."""
        for block in self.blocks:
            yield from block.get_constraint()

    def __iter__(self) -> Generator[Block, Any, None]:
        """Iterate all blocks in the behavior."""
        yield from self.blocks
        for disjunction in self.disjunctions:
            yield from disjunction.blocks

    def __len__(self):
        """Return the size of the current behavior."""
        return sum(len(block) for block in self.blocks)

    def __str__(self):
        """Return a string representation of the behavior."""
        return "\n".join([str(block) for block in chain(self.blocks, self.disjunctions)])

