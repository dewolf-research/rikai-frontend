"""Module dedicated to the export and visualization of typedb databases."""
from pathlib import Path
from rikai.data.database import Database


class DatabasePlotter:
    """Class dedicated to creating dotviz plots from a given database."""

    PROLOGUE = "strict digraph {\n"
    EPILOGUE = "}"

    def plot(self, db: Database) -> str:
        """Generate string lines in dot-format for the given database."""
        yield self.PROLOGUE
        for iid, label in db.get_calls():
            yield f'"{iid}" [label="{label}", shape="box"];'
        for iid, value in db.get_literals():
            yield f'"{iid}" [label="{value}"];'
        for param_id, call_id, index in db.get_parameters():
            yield f'"{param_id}" -> "{call_id}" [label="{index}"];'
        yield self.EPILOGUE

    def save(self, db: Database, path: Path):
        """Generate a plot of the given db and save it at the given path."""
        with path.open('w') as outfile:
            outfile.write("\n".join(self.plot(db)))


from rikai.data.database import DatabaseManager
db_name = "38dabdbb-82f3-41d0-8eb3-ca6649ee324e"
manager = DatabaseManager("localhost", 1729)
db = manager.get(db_name)

DatabasePlotter().save(db, Path("/home/nb/workspace/rikai/frontend/test.dot"))
