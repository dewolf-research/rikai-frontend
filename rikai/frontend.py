"""Module implementing various frontends for rikai."""
from abc import ABC
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Generator, Tuple

from rikai.data.database import DatabaseManager
from rikai.data.joernbridge import JoernBridge
from rikai.matcher import PatternMatcher
from rikai.pattern import Rule, RuleParser


class FrontendInterface(ABC):
    """Basic interface for all frontend implementations."""

    def __init__(self, config: Path = Path("config.ini")):
        """
        Create a new frontend instance based on the given config.
        :param config: The path to the config file.
        """
        self._config = ConfigParser()
        self._config.read(config)
        self._bridge = JoernBridge(Path(self._config.get("rikai", "Path")))
        self._manager = DatabaseManager(self._config.get("typedb", "Hostname"), int(self._config.get("typedb", "Port")))
        self._parser = RuleParser()

    def _preprocess(self, sample: Path) -> str:
        """Preprocess the file at the given path utilizing the JoernBridge."""
        return self._bridge.process_source(Path(sample))


class SynchronousFrontend(FrontendInterface):
    """Blocking frontend for local usage."""

    def analyze(self, sample: Path) -> Generator[Tuple[Rule, Tuple[Tuple[int, ...], ...]], Any, None]:
        """
        Analyze the given file.
        :param sample: The path to the file to be analyzed.
        :return: A dictionary mapping the matched rules to the matching lines.
        """
        db_name = self._preprocess(sample)
        db = self._manager.get(db_name)
        matcher = PatternMatcher(db)
        for rule in self._parser.iterate(Path(self._config.get("rules", "Path"))):
            result = matcher.match(rule.pattern)
            if result:
                yield rule, result

    def report_live(self, sample: Path):
        """Analyze the file while reporting matches on the go."""
        for rule, matches in self.analyze(sample):
            print(f"{rule.name} matched at {matches}")

    def report_dict(self, sample: Path) -> list:
        """Analyze the file and return a list with the results for json exports."""
        return [rule.to_dict() | {"matches": matches} for (rule, matches) in self.analyze(sample)]  # type: ignore
