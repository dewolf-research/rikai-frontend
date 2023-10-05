"""Module handling the generation of TypeDB queries."""
from typing import Any, Callable, Dict, Generator

from rikai.pattern import (
    Assignment,
    Block,
    Call,
    CallAssignment,
    IntegerLiteral,
    Literal,
    LiteralAssignment,
    Operand,
    Reference,
    Statement,
    StringLiteral,
    UnboundVariable,
    Variable,
)


class QueryGenerator:
    """Static class handling the generation of TypeDB queries."""

    Translators: Dict[type[Statement] | type[Operand], Callable] = {
        StringLiteral: lambda x: f'{hash(x)} isa StringLiteral, has StringValue "{x.value}"',
        IntegerLiteral: lambda x: f"{hash(x)} isa IntegerLiteral, has IntegerValue {x.value}",
        Call: lambda x: f"{id(x)} isa Call, has Label {x.label}",
        Reference: lambda x: QueryGenerator.Translators[x.literal.__class__](x.literal),
        LiteralAssignment: lambda x: QueryGenerator.Translators[x.literal.__class__](x.literal),
    }

    def generate(self, block: Block) -> str:
        """Generate a query matching the given block."""
        return "\n".join(self._generate_query(block))

    def _generate_query(self, block: Block) -> Generator[str, Any, None]:
        """
        Yield queries for each statement in the block, tracking the lines of Call matches.

        :param block: The block to be processed.
        :return: Strings making up the query.
        """
        yield "match"
        for call in block.calls:
            yield f'{id(call)} isa Call, has Label "{call.label}", has Line $l{id(call)};\n'
            yield from self._add_parameters(block, call)
        for reference in block.references:
            yield self.translate_literal(reference.literal)
        yield "get " + ", ".join(f"$l{id(call)}" for call in block.calls) + ";"

    def _add_parameters(self, block: Block, call: Call) -> Generator[str, Any, None]:
        """
        Generate strings as constraints about the parameters of the given statement.

        :param block: The block object containing the statement.
        :param call_name: String identifier of the parent Call entity.
        :param statement: The statement those parameters should be processed.
        :return: Strings describing the parameters and their relation to the call.
        """
        for j, parameter in enumerate(call.parameters):
            if isinstance(parameter, UnboundVariable):
                continue
            if isinstance(parameter, Variable):
                if definition := block.get_definition(parameter):
                    yield self.translate_definition(definition)
            elif isinstance(parameter, Literal):
                yield self.translate_literal(parameter)
            yield f"({parameter.name}_{j}, {call.name}) isa Parameter, has Index {j + 1};"

    @staticmethod
    def translate_literal(entity: Literal) -> str:
        """Generate a typedb query for the given operand, asserting its existence in the database."""
        match entity:
            case StringLiteral(value):
                return f'{id(entity)} isa StringLiteral, has StringValue "{value}";'
            case IntegerLiteral(value):
                return f"{id(entity)} isa IntegerLiteral, has IntegerValue {value};"
        raise ValueError(f"Unknown operand type {type(entity)}")

    def translate_definition(self, definition: Assignment) -> str:
        """Generate a constraint for the given value definition."""
        if isinstance(definition, CallAssignment):
            return f'{id(definition)} isa Call, has Label "{definition.value.label}";'
        if isinstance(definition, LiteralAssignment):
            return self.translate_literal(definition.value)
        raise ValueError(f"Unknown assignment type {type(definition)}")
