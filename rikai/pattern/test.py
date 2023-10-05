from lark import Lark

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
test32 = "test string"
foo("bar")
"""

with open('grammar.ebnf', 'r') as grammar:
    parser = Lark(grammar, start="rule")
tree = parser.parse(test)
print(tree.pretty())

print(tree)
print(dir(tree))
print(type(tree.data))
print(tree.children)