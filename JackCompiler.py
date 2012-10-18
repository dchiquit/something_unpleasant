#PSEUDOCODE TIME:

#For turning trees into vm code
def translate(node):
	for k in node.children:
		translate(k)
	if node.type == "integerConstant":
		out += ("push " + value)
	else if node.type == "stringConstant":
                #TODO
        else if node.type == "keywordConstant":
                #TODO
	else if node.type == "varName":
		variable = check_table(node.value)
		out += ("push " + location)
	else if node.type == "varName[expression]":
                #TODO
                
	else if node.type == "op":
		if node.value == "+":
			out += "add"
		else if node.value == "-":
			out += "sub"
		else if node.value == "*":
			out += "call Math.multiply 2"
		else if node.value == "/":
			out += "call Math.divide 2"
		else if node.value == "&":
			out += "and"
		else if node.value == "|":
			out += "or"
		else if node.value == "<":
			out += "lt"
		else if node.value == ">":
			out += "gt"
		else if node.value == "=":
			out += "eq"
	else if node.type == "(expression)":
                #TODO
	else if node.type == "unaryOp":
		if node.value == "-":
                        out += "neg"
                else if node.value == "~":
                        out += "not"
	else if node.type == "subroutineCall":
                out += ("call " + node.value + len(node.children))
	out += "\n"

"""This is assuming that the symbol table is passed to this script as a
list of hashtables with lowest scope first and is called table
"""
def check_table(key):
	condition = true
	index = 0
	while(condition):
		if (key in table[index]):
			return table[index][key]
		else:
			index++
