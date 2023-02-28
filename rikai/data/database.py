"""Module handling connections and sessions from typeDB."""
from typing import Any, Dict, Generator, Tuple

from typedb.client import SessionType, Thing, TransactionType, TypeDB, TypeDBSession  # type: ignore


class Database:
    """Class modelling a TypeDBSession instance."""

    def __init__(self, session: TypeDBSession):
        """Create a new Database based on the given session."""
        self._session = session

    def query(self, query: str) -> Tuple[Dict[str, Thing]]:
        """
        Send the given query to the database.
        :param query: The string query to be send.
        :return: A tuple of result mappings, mapping variable names to Thing instances.
        """
        with self._session.transaction(TransactionType.READ) as transaction:
            result = transaction.query().match(query)
            return [x.map() for x in result]  # type: ignore

    def get_calls(self) -> Generator[Thing, Any, None]:
        for mapping in self.query("match $x isa Call, has Label $y;"):
            yield mapping["x"].get_iid(), mapping["y"]._value

    def get_literals(self) -> Generator[Thing, Any, None]:
        for mapping in self.query("match $x isa Literal, has StringValue $y;"):
            yield mapping["x"].get_iid(), mapping["y"]._value

    def get_parameters(self) -> Generator[Tuple[str, str, int], Any, None]:
        for mapping in self.query("match $x (Source: $p, Sink: $c) isa Parameter, has Index $i;"):
            yield mapping["p"].get_iid(), mapping["c"].get_iid(), mapping["i"]._value

    def __del__(self):
        """Close the session when the object is deconstructed."""
        self._session.close()


class DatabaseManager:
    """Class managing a connection to a TypeDB server."""

    def __init__(self, hostname: str, port: int):
        """
        Create a manager for database objects handling TypeDB.
        :param hostname: The hostname of the server to connect to.
        :param port: The port to connect on.
        """
        self._client = TypeDB.core_client(f"{hostname}:{port}")

    def get(self, name: str) -> Database:
        """
        Get the database with the given name.
        :param name: The name of the database.
        :return: The database object requested.
        """
        assert self._client.databases().contains(name), f"Database {name} does not exist!"
        return Database(self._client.session(name, SessionType.DATA))

    def __del__(self):
        """Close the connection when the manager is deconstructed."""
        self._client.close()
