from JackConstants import *

from JackTokenizer import *

from JackParser import *

from JackExpressionTree import *

from JackErrors import *


class translator:
        def __init__(self, _classAddresses):
                self.labelCount = 0
                self.out = ""
                self.classAddresses = _classAddresses
                   
        def translateRoot(self, node):
                print node
                print "starts",node.children
                for k in node.children:
                        print "first CHILD"
                        print(self.translate(k))
                print "done"
        
        def translate(self, node):
                print(node.properties, node.children)
                if node.properties["type"] == 'ifStatement':
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
                elif node.properties["type"] == 'letStatement':
                        #no value, two children, first is variable identifier, second is expression
                        node.children[0] 
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
                        pass
                elif node.properties["type"] == 'class':
                        #This does not generate code, children of node is code of class
                        for k in node.children:
                                t = self.translate(k)
                elif node.properties["type"] == 'functionCall':
                        #value of function name, children include the arguments passed to the functionCall
                        self.out += ("call " + node.properties["name"] + " " + len(node.children) + "\n")
                elif node.properties["type"] == 'subroutine':
                        #value of function name, children is statementList of code
                        self.out += ("function " + node.properties["name"] + " " + str(node.properties["localVarCount"]) + "\n")
                elif node.properties["type"] == 'operator':
                        #value of whatever operator it is. Children are operand expressions
                         if node.properties["name"] == '+':
                                 self.out += "add\n"
                         elif node.properties["name"] == '-':
                                 self.out += "sub\n"
                         elif node.properties["name"] == '*':
                                 self.out += "call Math.multiply 2\n"
                         elif node.properties["name"] == '/':
                                 self.out += "call Math.divide 2\n"
                         elif node.properties["name"] == '&':
                                 self.out += "and\n"
                         elif node.properties["name"] == '|':
                                 self.out += "or\n"
                         elif node.properties["name"] == '<':
                                 self.out += "lt\n"
                         elif node.properties["name"] == '>':
                                 self.out += "gt\n"
                         elif node.properties["name"] == '=':
                                 self.out += "eq\n"
                                #when used for assignment, handled by letStatement node
                elif node.properties["type"] == "unaryOperator":
                        #value of whatever operator it is. Child is operand expression
                        if node.properties["name"] == '~':
                                self.out += "not\n"
                        if ndoe.value == '-':
                                self.out += "neg\n"
                elif node.properties["type"] == 'integerConstant':
                        #value of integer. No children.
                        self.out += ("push constant " + node.properties["name"] + "\n")
                elif node.properties["type"] == 'StringConstant':
                        #value of string. No children.
                        pass
                elif node.properties["type"] == 'KeywordConstant':
                        #value of keyword (true, false, null, this). No children.
                        pass
                elif node.properties["type"] == 'expression':
                        pass
                elif node.properties["type"] == 'root':
                        pass
                        #root: no value, children are class nodes
                elif node.properties["type"] == 'statementList':
                        pass
                        #no value, children are lines of code
                print "THIS IS "+self.out


if __name__=="__main__":
        tokenizer = Tokenizer("""
        class Wassup {
        field int test, test3, test4, test5;
        field int test2;
        static int test421;
        
        method int testanotherthing(int a, String b) {
            var int fs;
        }
        }""")
        jp = JackParser(tokenizer)
        #print(jp.parseAll()[0])
        parsed = jp.parseAll()
        trans  = translator(parsed[1])
        print("\n\n\nSTARTING ANEW\n\n\n")
        print(trans.translateRoot(parsed[0]))
        #translateRoot(parsed[0], parsed[1])
