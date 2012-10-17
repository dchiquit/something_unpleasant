# Teh comment

"""

class Node:
    [] children
    Node parent
    "" value
    "" type

class Parser:
    {} class_variables
    {} static_variables
    {} function_arguments
    {} function_locals
    ^one of these would have type, index (number)

"""
keyword: ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this' , 'let', 'do', 'if', 'else', 'while', 'return']
symbol: ['{' , '}' , '(' , ')' , '[' , ']' , '. ' , ',' , '; ' , '+' , '-' , '*' , '/' , '&' , ',' , '<' , '>' , '=' ,  '~' ]

class Tokenizer:
    
    def __init__(self, file):
        self.file = file
        self.tokens = []
		_preprocess()
	
	def _preprocess(self):
		pass

    def popToken(self):
        self.tokens = [(type,value)] + self.tokens
        return (type, value)

    def pushToken(self):
        self.file = self.tokens[0][1] + self.file
        self.tokens = self.tokens[1:]


