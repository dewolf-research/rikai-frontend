"""Module handling the generation of TypeDB queries."""
from typing import Any, Generator

from rikai.pattern import Behavior, Literal, UnboundVariable, Variable


class QueryGenerator:
    """Static class handling the generation of TypeDB queries."""

    @staticmethod
    def generate(behavior: Behavior) -> str:
        """Generate a query matching the given behavior."""
        return "\n".join(QueryGenerator._generate_query(behavior))

    @staticmethod
    def _generate_query(behavior: Behavior) -> Generator[str, Any, None]:
        """
        Yield queries for each statement in the behavior, tracking the lines of Call matches.

        :param behavior: The behavior to be processed.
        :return: Strings making up the query.
        """
        yield "match"
        for i, statement in enumerate(behavior.statements):
            call_name = f"$call{i}"
            yield f'{call_name} isa Call, has Label "{statement.label}", has Line $l{i};\n'
            yield from QueryGenerator._add_parameters(behavior, call_name, statement)
        yield "get " + ", ".join(f"$l{i}" for i in range(len(behavior.statements))) + ";"

    @staticmethod
    def _add_parameters(behavior, call_name, statement) -> Generator[str, Any, None]:
        """
        Generate strings as constraints about the parameters of the given statement.

        :param behavior: The behavior object containing the statement.
        :param call_name: String identifier of the parent Call entity.
        :param statement: The statement those parameters should be processed.
        :return: Strings describing the parameters and their relation to the call.
        """
        for j, parameter in enumerate(statement.parameters):
            if isinstance(parameter, UnboundVariable):
                continue
            yield f"({call_name}_{j}, {call_name}) isa Parameter, has Index {j + 1};"
            if isinstance(parameter, Literal):
                yield f'{call_name}_{j} isa Literal, has StringValue "{str(parameter)}";'
            elif isinstance(parameter, Variable) and (definition := behavior.get_definition(parameter)):
                yield f'{call_name}_{j} isa Call, has Label "{definition.label}";'
