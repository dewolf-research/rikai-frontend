from lark import Lark

from parser import LarkParser, RuleParser

test = """
y = 2
switch ( "method" ) {
    case "lol":
        x = 1
        break
    case "test":
        x = 3
        break
}
if ( x )
test32 = "test string"
foo("bar")
"""

parser = RuleParser()
pattern = parser.parse_pattern(test)
print(str(pattern))

for possibility in pattern.expand():
    print(possibility)
    for constraint in possibility.get_constraint():
        print(constraint)