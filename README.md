# Rikai
[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
![loc](https://img.shields.io/tokei/lines/github/dewolf-research/rikai-frontend)
![license](https://img.shields.io/github/license/dewolf-research/rikai-frontend)
![release](https://img.shields.io/github/v/release/dewolf-research/rikai-frontend)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![pydocstyle](https://img.shields.io/badge/pydocstyle-checked-AD4CD3)](http://www.pydocstyle.org/en/stable/)
[![pydocstyle](https://img.shields.io/badge/pycodestyle-checked-AD4CD3)](http://www.pydocstyle.org/en/stable/)


Allows to match rules on fuzzy c code utilizing typeDB pattern matching.

## Setup
Check out `config.ini` for all configuration options.
In order to get started, set up the path to `joern-rikai` and the location a typeDB server.
Alternatively, you can download the latest version of rikai-joern by running `setup.sh` and
you can bootstrap the typeDB server by running `podman run --name typedb -d -p 1729:1729 vaticle/typedb:latest`.

If you want to use the container version of rikai, we recommend utilizing `docker-compose run --rm rikai`.

## Usage
You can run rikai from command line like this:

`./rikai-cmd.py <path>`

Check out `./rikai-cmd.py --help` for additional options.
