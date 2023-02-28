from pathlib import Path

from rikai.data.database import DatabaseManager
from rikai.data.joernbridge import JoernBridge
from rikai.matcher import PatternMatcher
from rikai.pattern import PatternParser


class TestRunner:
    pass


rule = """x = HttpOpenRequestA(_, _, _, _, _, _, _)
InternetCloseHandle(x)
"""
sample = "/home/nb/workspace/rikai/temp.c"
rikai_path = "/home/nb/workspace/rikai/standalone/target/universal/stage/bin/rikai"
host = "localhost"
port = 1729

pattern = PatternParser().parse_pattern(rule)

bridge = JoernBridge(Path(rikai_path))
db_name = bridge.process_source(Path(sample))

manager = DatabaseManager(host, port)
db = manager.get(db_name)

matcher = PatternMatcher(db)
result = matcher.match(pattern)
for match in result:
    print(f"match: {', '.join(str(line) for line in match)}")

del db
del manager
