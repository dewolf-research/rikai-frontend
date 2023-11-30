import pytest
from lark import Token

from rikai.pattern import IntegerLiteral, StringLiteral, Compound, Variable, Condition
from rikai.pattern.parser import LarkParser, RuleParser


class TestStatements:
    """Class in charge of testing the parsing of statement expressions."""

    @pytest.fixture(scope="module")
    def parser(self):
        return RuleParser(LarkParser(start="statement"))

    @pytest.mark.parametrize(
        "test,expected",
        [
            ("0x50", IntegerLiteral(0x50)),
            ("1337", IntegerLiteral(1337)),
            ("-8", IntegerLiteral(-8)),
            ("+50", IntegerLiteral(50)),
            ("0xFF", IntegerLiteral(0xff)),
            ("0xfF", IntegerLiteral(0xff))
    ])
    def test_integers(self, test, expected, parser):
        assert parser.parse(test, "operand") == expected

    @pytest.mark.parametrize(
        "test,expected",
        [
            ('"test"', Token('ESCAPED_STRING', '"test"')),
            ('"0x42"', Token('ESCAPED_STRING', '"0x42"')),
    ])
    def test_string(self, test, expected):
        assert LarkParser(start="operand").parse(test, "operand") == expected

    @pytest.mark.parametrize(
        "test,expected",
        [
            ("x2", Variable("x2")),
            ("10test", Variable("10test")),
            ('test', Variable("test")),
    ])
    def test_variable(self, test, expected, parser):
        assert parser.parse(test, "operand") == expected

    @pytest.mark.parametrize(
        "test,expected",
        [
            ("2 + 2", Compound((IntegerLiteral(2), IntegerLiteral(2)))),
            ("2 + a", Compound((IntegerLiteral(2), Variable("a")))),
            ("a + a", Compound((Variable("a"), Variable("a")))),
            ('"a" + "b"', Compound((StringLiteral("a"), StringLiteral("b")))),
            ("a + 1 + 1", Compound((Variable("a"), IntegerLiteral(1), IntegerLiteral(1)))),
            ("-1 + -2", Compound((IntegerLiteral(-1), IntegerLiteral(-2)))),
            ('"test" + 1', Compound((StringLiteral("test"), IntegerLiteral(1)))),

    ])
    def test_compound(self, test, expected, parser):
        assert parser.parse(test, "operand") == expected

    @pytest.mark.parametrize(
        "test,expected",
        [
            ("2 | 2", Condition((IntegerLiteral(2), IntegerLiteral(2)))),
            ("2 | a", Condition((IntegerLiteral(2), Variable("a")))),
            ("a | a", Condition((Variable("a"), Variable("a")))),
            ('"a" | "b"', Condition((StringLiteral("a"), StringLiteral("b")))),
            ("a | 1 | 1", Condition((Variable("a"), IntegerLiteral(1), IntegerLiteral(1)))),
            ("-1 | -2", Condition((IntegerLiteral(-1), IntegerLiteral(-2)))),
            ('"test" | 1', Condition((StringLiteral("test"), IntegerLiteral(1)))),

    ])
    def test_condition(self, test, expected, parser):
        assert parser.parse(test, "operand") == expected
