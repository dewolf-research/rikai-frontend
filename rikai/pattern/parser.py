"""Module implementing the parsing of pattern and rules from strings."""
from pathlib import Path
from re import compile
from typing import Any, Generator, Iterable, Tuple

from yaml import safe_load

from .behavior import Behavior, Block, Disjunction
from .operands import Literal, Operand, UnboundVariable, Variable
from .rule import Rule
from .statement import Assignment, Call


class PatternParser:
    """Class in charge of parsing pattern and their nested objects."""

    REGEX_STATEMENTS = compile(r"(?:(?P<defines>[\w ,]+) = )?(?P<label>[\w@!-_]+)\((?P<parameters>[\w\- ,:\"]+)?\)")

    def parse_block(self, lines: Iterable[str]) -> Block:
        """Generate a block from an iterable returning strings."""
        return Block(tuple(self.parse_statement(line) for line in lines))

    def parse_disjunction(self, disjunction: dict) -> Disjunction:
        """Parse the given disjunction, generating a nested tuple of statements."""
        assert "or" in disjunction, f"Malformed disjunction {disjunction}!"
        return Disjunction(
            {
                name: Block(tuple(self.parse_statement(statement) for statement in alternative))
                for name, alternative in disjunction["or"].items()
            }
        )

    def parse_behavior(self, lines: Tuple[str | Tuple[str, ...], ...]) -> Behavior:
        """Generate a behavior from an string iterable."""
        return Behavior(
            Block(tuple(self.parse_statement(line) for line in lines if isinstance(line, str))),
            tuple(self.parse_disjunction(line) for line in lines if isinstance(line, dict)),
        )

    def parse_statement(self, text: str) -> Call:
        """Parse a statement from the given string."""
        regex_match = self.REGEX_STATEMENTS.match(text)
        if not regex_match:
            raise ValueError('Can not parse Statement: "%s"' % text)
        values = regex_match.groupdict("")
        parameters = self._parse_parameters(values["parameters"])
        if values["defines"]:
            return Assignment(values["label"], parameters, Variable(values["defines"]))
        return Call(values["label"], parameters)

    def _parse_parameters(self, text: str) -> Tuple[Operand, ...]:
        """Parse the parameter string, checking for the presence of indices."""
        tokens = (parameter.strip() for parameter in filter(None, text.split(",")))
        if ":" not in text:
            return tuple(self._parse_operand(token) for token in tokens)
        params = {index: operand for index, operand in (self._parse_index_operand(token) for token in tokens)}
        last_index = max(params.keys())
        return tuple(params[i] if i in params else UnboundVariable() for i in range(1, last_index + 1))

    def _parse_operand(self, text: str) -> Operand:
        """Parse an operand from the given string."""
        if text == UnboundVariable.SYMBOL:
            return UnboundVariable()
        elif text.startswith('"'):
            return Literal(text.strip('"'))
        else:
            return Variable(text)

    def _parse_index_operand(self, text: str) -> Tuple[int, Operand]:
        """Parse an indexed operand in the form of <index>:<operand>."""
        assert ":" in text, f"Malformed indexed operand: {text}"
        index_string, operand_token = text.split(":", 2)
        return int(index_string), self._parse_operand(operand_token)


class RuleParser:
    """Class dedicated to parse rule definitions from yaml files."""

    def __init__(self):
        """Generate a new RuleParser instance."""
        self._parser = PatternParser()

    def iterate(self, path: Path) -> Generator[Rule, Any, None]:
        """
        Iterate all rules in the given directory and its subdirectories.

        :param path: The path to the root rule directory.
        :return: Yield all rules found.
        """
        for sub_path in path.rglob("*.yaml"):
            yield self.parse_file(sub_path)

    def parse_file(self, path: Path) -> Rule:
        """
        Parse the given file and return the contained rules.

        :param path: The path to the yaml file to be parsed.
        :return: The rules contained.
        """
        with path.open("r") as source:
            data = safe_load(source)
        assert "pattern" in data, f"Malformed rule file {path}"
        return self.parse_rule(data)

    def parse_rule(self, data: dict) -> Rule:
        """
        Parse the given rule from the given dictionary.

        :param data: A dict containing a 'name', 'meta' and 'pattern' field.
        :return: The corresponding Rule object.
        """
        return Rule(data["name"], data["meta"], self._parser.parse_behavior(data["pattern"]))
