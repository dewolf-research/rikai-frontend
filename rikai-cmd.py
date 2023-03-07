#!/usr/bin/env python3
"""Class implementing the command line interface of rikai."""
from argparse import ArgumentParser, Namespace
from json import dumps
from pathlib import Path

from rikai.frontend import SynchronousFrontend


class CommandLineInterface:
    """Main class to handle command line usage."""

    def __init__(self, _options: Namespace, frontend=SynchronousFrontend):
        """Create a new interface using the given command line options."""
        self._options = _options
        self._frontend = frontend(options.config)

    def run(self):
        """Run rikai with the passed options."""
        if self._options.json:
            print(dumps(self._frontend.report_dict(options.source), indent=2))
        else:
            self._frontend.report_live(options.source)


# Handles direct script execution utilizing argparse
if __name__ == "__main__":
    parser = ArgumentParser("rikai", description="Match behavior pattern in fuzzy C source files.")
    parser.add_argument("source", type=Path, help="Path to the source file to be analyzed.")
    parser.add_argument(
        "--config",
        "-d",
        type=Path,
        default=Path(__file__).absolute().parent / "rikai/config.ini",
        help="The path to the config file to be used.",
    )
    parser.add_argument("--json", dest="json", action="store_true", help="Flag for generating json output.")
    options = parser.parse_args()
    CommandLineInterface(options).run()
