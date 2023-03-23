"""Module implementing the parsing of pattern and rules from strings."""
from pathlib import Path
from re import compile
from typing import Any, Dict, Generator, Iterable, Optional, Tuple

from yaml import safe_load

from .behavior import Behavior, Block, Disjunction
from .operands import EnumValue, IntegerLiteral, Literal, Operand, StringLiteral, UnboundVariable, Variable
from .rule import Rule
from .statement import Assignment, Call, CallAssignment, LiteralAssignment, Statement


class PatternParser:
    """Class in charge of parsing pattern and their nested objects."""

    REGEX_ASSIGNMENT = compile(r"(?P<lhs>\w+) = (?P<rhs>[\S ]+)")
    REGEX_CALL = compile(r"(?P<label>[\w@!-_]+)\((?P<parameters>[\w\- ,:\"]+)?\)")

    def __init__(self, definition: Dict[str, int]):
        """Generate a new PatternParser instance."""
        self._definitions = definition

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

    def parse_statement(self, text: str) -> Statement:
        """Parse a statement from the given string."""
        if " = " in text:
            return self.parse_assignment(text)
        return self.parse_call(text)

    def parse_assignment(self, text: str) -> Assignment:
        """Parse an assignment from the given string."""
        if not (match := self.REGEX_ASSIGNMENT.match(text)):
            raise ValueError(f'Malformed call: "{text}"')
        values = match.groupdict("")
        if self._could_be_call(match.group("rhs")):
            return CallAssignment(Variable(values["lhs"]), self.parse_call(values["rhs"]))
        return LiteralAssignment(Variable(values["lhs"]), self.parse_literal(values["rhs"]))

    def parse_call(self, text: str) -> Call:
        """Parse a call statement from the given string."""
        if not (match := self.REGEX_CALL.match(text)):
            raise ValueError(f'Malformed call: "{text}"')
        values = match.groupdict("")
        return Call(values["label"], self._parse_parameters(values["parameters"]))

    def parse_literal(self, text: str) -> Literal:
        """Parse a literal (e.g. integer or string) from the given string."""
        if text in self._definitions:
            return EnumValue(self._definitions[text], text)
        if text.startswith('"'):
            return StringLiteral(text.strip('"'))
        if text.isnumeric():
            return IntegerLiteral(int(text))
        raise ValueError(f'"{text}" is not a valid literal!')

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
        try:
            return self.parse_literal(text)
        except ValueError as e:
            return Variable(text)

    def _parse_index_operand(self, text: str) -> Tuple[int, Operand]:
        """Parse an indexed operand in the form of <index>:<operand>."""
        assert ":" in text, f"Malformed indexed operand: {text}"
        index_string, operand_token = text.split(":", 2)
        return int(index_string), self._parse_operand(operand_token)

    @staticmethod
    def _could_be_call(text: str) -> bool:
        """Check whether the given string could be a call."""
        return not text.startswith('"') and "(" in text


class RuleParser:
    """Class dedicated to parse rule definitions from yaml files."""

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
        parser = PatternParser(data["definitions"] if "definitions" in data else {})
        return Rule(data["name"], data["meta"], parser.parse_behavior(data["pattern"]))
