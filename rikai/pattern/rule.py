"""Module implementing the Rule class."""
from dataclasses import dataclass
from typing import Dict

from .behavior import Behavior


@dataclass(frozen=True)
class Rule:
    """Class modelling a pattern with a name and metadata."""

    name: str
    meta: Dict[str, str]
    pattern: Behavior

    def to_dict(self) -> dict:
        """Return a dict-representation of the rule."""
        return {"name": self.name, "meta": self.meta, "pattern": str(self.pattern)}
