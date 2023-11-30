"""Module implementing the parsing of pattern and rules from strings."""
from typing import Tuple, Generator, Any, Optional
from pathlib import Path

from lark import Lark, Tree, Transformer, v_args
from yaml import safe_load

from rikai.pattern.behavior import Behavior, Disjunction
from rikai.pattern.block import Block, Branch, Loop
from rikai.pattern.operands import EnumValue, IntegerLiteral, Literal, Operand, StringLiteral, UnboundVariable, Variable
from rikai.pattern.operations import Compound, Condition
from rikai.pattern.rule import Rule
from rikai.pattern.statement import Assignment, Call, CallAssignment, LiteralAssignment, Reference, Statement


class LarkParser:
    """Wrapper for a lark parser based on the predefined grammar."""

    def __init__(self, grammar_file: Optional[Path] = None, start: str = 'behavior'):
        """Create a new instance, parsing the set grammar."""
        if not grammar_file:
            grammar_file = Path(__file__).parent / 'grammar.ebnf'
        with grammar_file.open('r') as grammar:
            self.parser = Lark(grammar, start=start)
        print(start)
        print(self.parser)

    def parse(self, text: str, start: str = 'behavior') -> Tree:
        """Parse a tree object from the given string."""
        return self.parser.parse(text, start)


class RuleParser:
    """Class dedicated to parse rule definitions from yaml files."""

    def __init__(self, parser: Optional[LarkParser] = None):
        """initialize a new RuleParser object."""
        self._parser = parser if parser else LarkParser()
        self._transformer = LarkTransformer()

    def iterate(self, path: Path) -> Generator[Rule, Any, None]:
        """
        Iterate all rules in the given directory and its subdirectories.

        :param path: The path to the root rule directory.
        :return: Yield all rules found.
        """
        for sub_path in path.rglob("*.yml"):
            print(sub_path)
            yield self.parse_file(sub_path)

    def parse(self, text: str, start: str):
        """
        Utilize parser and Transformer on the given string.

        :param text: The text to be parsed.
        :param start: The start object of the parser.
        """
        tree = self._parser.parse(text, start)
        print(tree, type(tree))
        return self._transformer.transform(tree)

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
        pattern = self._transformer.transform(self._parser.parse(data["pattern"]))
        return Rule(data["name"], data["meta"], pattern)

    def parse_pattern(self, text: str) -> Behavior:
        """
        Parse a behavior pattern from the given string.

        :param text: The text to be parsed
        :return: A behavior object.
        """
        return self.parse(text, "behavior")


@v_args(inline=True)
class LarkTransformer(Transformer):
    """Class transforming the parsed Lark Tree into pattern."""

    def behavior(self, *blocks: Block | Disjunction) -> Behavior:
        return Behavior(
            tuple(block for block in blocks if not isinstance(block, Disjunction)),
            tuple(block for block in blocks if isinstance(block, Disjunction))
        )

    def block(self, *statements: Statement) -> Block:
        return Block(statements)

    def disjunction(self, value: str, *cases: Tuple[str, Block]) -> Disjunction:
        return Disjunction(value, dict(cases))

    def case(self, value: str, block: Block) -> Tuple[str, Block]:
        return value, block

    def assignment(self, lhs: Variable, rhs: Call | Literal) -> Assignment:
        if isinstance(rhs, Call):
            return CallAssignment(lhs, rhs)
        return LiteralAssignment(lhs, rhs)

    def variable(self, name: str) -> Variable:
        return Variable(str(name))

    def call(self, label: str, *parameter: Operand):
        return Call(label, parameter)

    def compound(self, *operands: Operand):
        return Compound(operands)

    def condition(self, *operands: Operand):
        return Condition(operands)

    def ESCAPED_STRING(self, string: str) -> StringLiteral:
        return StringLiteral(string.strip('"'))

    def branch(self, condition: Condition, *statements: Statement) -> Branch:
        return Branch(statements, condition)

    def loop(self, condition: Condition, *statements: Statement) -> Loop:
        return Loop(statements, condition)

    def integer(self, *digits: str) -> IntegerLiteral:
        return IntegerLiteral(int(''.join(digits), 0))

    def reference(self, literal: Literal) -> Reference:
        return Reference(literal)

    # Literal transformation.

    name = str
    SIGNED_NUMBER = str
    HEXDIGIT = str
    unbound = UnboundVariable
