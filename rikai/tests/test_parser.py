"""Module implementing tests for parsing behavior pattern from text."""
import pytest
from rikai.pattern import Assignment, Call, Literal, PatternParser, UnboundVariable, Variable


class TestParser:
    """Implements tests for parsing patterns and their components from strings."""

    @pytest.mark.parametrize(
        "input,output",
        [
            ("x", Variable("x")),
            ("awd812_dwdw", Variable("awd812_dwdw")),
            ("0x1337", Variable("0x1337")),
            ("_", UnboundVariable()),
            ('"_"', Literal("_")),
            (
                '"This could be quiet a long string! With sp€c1äl chars and everything!"',
                Literal("This could be quiet a long string! With sp€c1äl chars and everything!"),
            ),
        ],
    )
    def test_parse_operand(self, input, output):
        """Test parsing operands from text strings."""
        assert PatternParser()._parse_operand(input) == output

    @pytest.mark.parametrize(
        "input,index,output",
        [
            ("1:x", 1, Variable("x")),
            ("100:0x1337", 100, Variable("0x1337")),
            ("1:_", 1, UnboundVariable()),
            ('4:"_"', 4, Literal("_")),
        ],
    )
    def test_parse_indexed_operand(self, input, index, output):
        """Test if indexed parameters are parsed correctly."""
        assert PatternParser()._parse_index_operand(input) == (index, output)

    @pytest.mark.parametrize(
        "input,output",
        [
            ("foo()", Call("foo", tuple())),
            ('b64foo("test")', Call("b64foo", tuple((Literal("test"),)))),
            (
                '213412("0", 0)',
                Call(
                    "213412",
                    tuple(
                        (
                            Literal("0"),
                            Variable("0"),
                        )
                    ),
                ),
            ),
            (
                'foo(2:"test", 4:x0)',
                Call(
                    "foo",
                    tuple(
                        (
                            UnboundVariable(),
                            Literal("test"),
                            UnboundVariable(),
                            Variable("x0"),
                        )
                    ),
                ),
            ),
        ],
    )
    def test_parse_calls(self, input, output):
        """Test the parsing of calls from raw text strings."""
        assert PatternParser().parse_statement(input) == output

    @pytest.mark.parametrize(
        "input,output",
        [
            ("x = foo()", Assignment("foo", tuple(), Variable("x"))),
            ('x123 = foo("test")', Assignment("foo", tuple((Literal("test"),)), Variable("x123"))),
        ],
    )
    def test_parse_assignments(self, input, output):
        """Test the parsing of assignments from text."""
        assert PatternParser().parse_statement(input) == output
