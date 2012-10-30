from JackConstants import *

from JackTokenizer import *

from JackParser import *

from JackExpressionTree import *

from JackErrors import *

import sys


conditionals = {"=":"eq", "<": "lt", ">": "gt", "&": "and"}


class translator:
        def __init__(self):
                self.labelCount = 0
                self.out = ""
                self.currentClass = ""
                self.currentFunction = ""
                self.classAddresses = {}
        def output(self):
                return self.out
        def setAddresses(self, ca):
                self.classAddresses = ca
        def translate(self, node):
                if node.properties["type"] == 'ifStatementWithElse':
                        #no value, first child is expression (must have), second child is statementList for expression true, third child is statementList for else
                        self.translate(node.children[0])
                        self.out += "not\n"
                        tempLabel = self.labelCount
                        self.labelCount += 2
                        self.out += ("if-goto L" + str(tempLabel) + "\n")
                        self.translate(node.children[1])
                        self.out += ("goto L" + str(tempLabel + 1) + "\n")
                        self.out += ("label L" + str(tempLabel) + "\n")
                        self.translate(node.children[2])
                        self.out += ("label L" + str(tempLabel + 1) + "\n")
                elif node.properties["type"] == 'ifStatement':
                        #no value, first child is expression (must have), second child is statementList for expression true
                        self.translate(node.children[0])
                        self.out += "not\n"
                        tempLabel = self.labelCount
                        self.labelCount += 1
                        self.out += ("if-goto L" + str(tempLabel) + "\n")
                        self.translate(node.children[1])
                        self.out += ("label L" + str(tempLabel) + "\n")
                elif node.properties["type"] == 'let':
                        #no value, two children, first is variable identifier, second is expression
                        #assuming type is integer
                        self.translate(node.children[1])
                        identifier = node.children[0].properties['value']
                        if (identifier in self.classAddresses[self.currentClass][self.currentFunction]):
                                self.out += ("pop " + str(self.classAddresses[self.currentClass][self.currentFunction][node.children[0].properties["value"]] + "\n"))
                        else:
                                self.out += ("pop " + str(self.classAddresses[self.currentClass]['$global'][node.children[0].properties["value"]] + "\n"))
                elif node.properties["type"] == "doStatement":
                        for child in node.children:
                                self.translate(child)
                        self.out += "pop temp 0\n"
                elif node.properties["type"] == 'identifier':
                        thingy = self.classAddresses[self.currentClass]
                        if node.properties['value'] in thingy[self.currentFunction]:
                                self.out += "push " + thingy[self.currentFunction][node.properties['value']] +"\n"
                        else:
                                self.out += "push " + thingy["$global"][node.properties['value']] +"\n"
                elif node.properties["type"] == 'whileStatement':
                        #no value, first child is expression, second child is statementList
                        tempLabel = self.labelCount
                        self.labelCount += 2
                        self.out += ("label L" + str(tempLabel) + "\n")
                        self.translate(node.children[0])
                        self.out += "not\n"
                        self.out += ("if-goto L" + str(tempLabel + 1) + "\n")
                        self.translate(node.children[1])
                        self.out += ("goto L" + str(tempLabel) + "\n")
                        self.out += ("label L" + str(tempLabel + 1) + "\n")
                elif node.properties["type"] == 'returnStatement':
                        #no value, first child is expression
                        if len(node.children) != 0:
                                identifier = node.children[0].properties['value']
                                if (identifier in self.classAddresses[self.currentClass][self.currentFunction]):
                                        self.out += ("push " + str(self.classAddresses[self.currentClass][self.currentFunction][node.children[0].properties["value"]] + "\n"))
                                elif (identifier in self.classAddresses[self.currentClass]['$global']):
                                        self.out += ("push " + str(self.classAddresses[self.currentClass]['$global'][node.children[0].properties["value"]] + "\n"))
                        else:
                            self.out += "push constant 0\n"
                        self.out += "return\n"
                elif node.properties["type"] == 'class':
                        #This does not generate code, children of node is code of class
                        self.currentClass = node.properties['name']
                        for k in node.children:
                                self.translate(k)
                elif node.properties["type"] == 'functionCall':
                        #value of function name, children include the arguments passed to the functionCall
                        for k in node.children:
                                self.translate(k)
                        self.out += ("call " + node.properties["value"] + " " + str(len(node.children)) + "\n")
                elif node.properties["type"] == 'subroutine':
                        #value of function name, children is statementList of code
                        self.currentFunction = node.properties['name']
                        self.out += ("function " + self.currentClass+"."+node.properties["name"] + " " + str(node.properties["localVarCount"]) + "\n")
                        if node.properties["functionType"] == "constructor":
                                self.out += "push constant "+str(len(self.classAddresses[self.currentClass]["$global"]))+"\n"
                                self.out += "call Memory.alloc 1\n"
                                self.out += "pop pointer 0\n"
                                #for glob in self.classAddresses[self.currentClass]["$global"]:
                                #    self.out += ""
                        elif node.properties["functionType"] == "method":
                                self.out += "push argument 0\npop pointer 0\n"
                        for k in node.children:
                                self.translate(k)
                        if node.properties["functionType"] == "constructor":
                                self.out = self.out[:-7] + "push pointer 0\nreturn\n"
                elif node.properties["type"] == 'binaryOperator':
                        self.translate(node.children[0])
                        self.translate(node.children[1])
                        #value of whatever operator it is. Children are operand expressions
                        if node.properties["value"] == '+':
                                self.out += "add\n"
                        elif node.properties["value"] == '-':
                                self.out += "sub\n"
                        elif node.properties["value"] == '*':
                                self.out += "call Math.multiply 2\n"
                        elif node.properties["value"] == '/':
                                self.out += "call Math.divide 2\n"
                        elif node.properties["value"] == '&':
                                self.out += "and\n"
                        elif node.properties["value"] == '|':
                                self.out += "or\n"
                        elif node.properties["value"] == '<':
                                self.out += "lt\n"
                        elif node.properties["value"] == '>':
                                self.out += "gt\n"
                        elif node.properties["value"] == '=':
                                self.out += "eq\n"
                               #when used for assignment, handled by letStatement node
                elif node.properties["type"] == "unaryOperator":
                        #value of whatever operator it is. Child is operand expression
                        if node.properties["value"] == '~':
                                self.out += "not\n"
                        if ndoe.value == '-':
                                self.out += "neg\n"
                elif node.properties["type"] == 'integerConstant':
                        #value of integer. No children.
                        self.out += ("push constant " + node.properties["value"] + "\n")
                        """
                elif node.properties["type"] == 'StringConstant':
                        #value of string. No children.
                        push constant len(node.properties['value'])
                        self.out += "call String.new 1"
                        for k in node.properties['value']:
                                if (k == "\b"):
                                        self.out += "call String.backspace 0\n"
                                if (k == "\""):
                                        self.out += "call String.doubleQuote 0\n"
                                if (k == "\n"):
                                        self.out += "call String.newLine 0\n"
                                else:
                                        self.out += "push constant " + str(ord(k)) + "\n"
                                self.out += "call appendChar 1"
                """
                elif node.properties["type"] == 'keywordConstant':
                        #value of keyword (true, false, null, this). No children.
                        if node.properties['value'] == 'true':
                                self.out += "push constant 1\n"
                        if node.properties['value'] == 'false':
                                self.out += "push constant 0\n"
                        if node.properties['value'] == 'null':
                                self.out += "push constant 0\n"
                        if node.properties['value'] == 'this':
                                self.out += "push pointer 0\n"
                elif node.properties["type"] == 'conditional':
                        self.translate(node.children[0])
                        self.translate(node.children[1])
                        self.out += conditionals[node.properties["value"]]+"\n"
                elif node.properties["type"] == 'root':
                        #root: no value, children are class nodes
                        for k in node.children:
                                self.translate(k)
                elif node.properties["type"] == 'statementList':
                        #no value, children are lines of code
                        for k in node.children:
                                self.translate(k)
                else:
                        print "FLAGGING THIS THANG! THIS IS A UNKNOWN OPERATOR! FIX ME PLEASE!"
                        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                        print node.properties["type"]



if __name__=="__main__":
        trans  = translator()
        
        for arg in sys.argv[1:-1]:
            squareFile = open(arg,"r")
            tokenizer = Tokenizer(squareFile.read())
            squareFile.close()
            jp = JackParser(tokenizer)
            #print(jp.parseAll()[0])
            parsed = jp.parseAll()
            trans.setAddresses(parsed[1])
            trans.translate(parsed[0])
        
            trans.out += "\n\n\n\n"
        
        
        print("\n\n\nSTARTING ANEW\n\n\n")
        
        fileout = open(sys.argv[-1],"w")
        fileout.write(trans.output())
        fileout.close()
        
        
        #translateRoot(parsed[0], parsed[1])
