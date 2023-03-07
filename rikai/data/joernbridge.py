"""Module handling the communication with the joern plugin."""
import sys
from pathlib import Path
from subprocess import CalledProcessError, run
from tempfile import NamedTemporaryFile
from uuid import uuid4


class JoernBridge:
    """Class managing communication with the joern-rikai-interface."""

    def __init__(self, path: Path, timeout: int = 120):
        """
        Create a new JoenBridge.

        :param path: The path to the rikai executable to be utilized.
        :param timeout: The timeout in seconds.
        """
        assert path.exists(), f"Could not find rikai executable at {path}!"
        self.rikai_path = path
        self.timeout = timeout

    def process_data(self, data: str) -> str:
        """
        Pass the given data to joern utilizing a temporary file.

        :param data: The source code to be passed.
        :return: The id of the created database.
        """
        with NamedTemporaryFile() as buffer:
            buffer.write(data.encode("utf-8"))
            return self.process_source(Path(buffer.name))

    def process_source(self, path: Path) -> str:
        """
        Use joern to process the given file.

        :param path: The path to the source file to be processed.
        :return: The id of the created database.
        """
        assert path.exists(), "The given source file does not exist!"
        database_id = str(uuid4())
        result = run((self.rikai_path, database_id, path), timeout=self.timeout, capture_output=True)
        try:
            result.check_returncode()
        except CalledProcessError as e:
            print(e.stderr.decode("utf-8"))
            sys.exit()
        return database_id
