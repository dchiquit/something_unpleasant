keyword = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this' , 'let', 'do', 'if', 'else', 'while', 'return', 'new']
symbol = ['{' , '}' , '(' , ')' , '[' , ']' , '.' , ',' , ';' , '+' , '-' , '*' , '/' , '&' , '<' , '>' , '=' ,  '~' ]
operations = ['+', '-', '*', '/', '&', '<', '>', '=', '~']
operators = [('symbol', op) for op in operations]

termination_token = ("eof", None)

IF_STATEMENT = 0
LET_STATEMENT = 1
WHILE_STATEMENT = 2
DO_STATEMENT = 3
RETURN_STATEMENT = 4
METHOD = 5


