from JackConstants import *

from JackTokenizer import *

from JackParser import *

from JackExpressionTree import *

from JackErrors import *


class translator:
        def __init__(_classAddresses):
                labelCount = 0
                out = ""
                classAddresses = addresses[node.properties['name']]
        def translate(node):
                print(node.properties, node.children)
                if node.properties["type"] == 'ifStatement':
                        #no value, first child is expression (must have), second child is statementList for expression true, third child is statementList for else
                        translate(node.children[0])
                        out += "not\n"
                        tempLabel = labelCount
                        labelCount += 2
                        out += ("if-goto L" + str(tempLabel) + "\n")
                        translate(node.children[1])
                        out += ("goto L" + str(tempLabel + 1) + "\n")
                        out += ("label L" + str(tempLabel) + "\n")
                        translate(node.children[2])
                        out += ("label L" + str(tempLabel + 1) + "\n")
                elif node.properties["type"] == 'letStatement':
                        #no value, two children, first is variable identifier, second is expression
                        node.children[0] 
                elif node.properties["type"] == 'whileStatement':
                        #no value, first child is expression, second child is statementList
                        tempLabel = labelCount
                        labelCount += 2
                        out += ("label L" + str(tempLabel) + "\n")
                        translate(node.children[0])
                        out += "not\n"
                        out += ("if-goto L" + str(tempLabel + 1) + "\n")
                        translate(node.children[1])
                        out += ("goto L" + str(tempLabel) + "\n")
                        out += ("label L" + str(tempLabel + 1) + "\n")
                elif node.properties["type"] == 'returnStatement':
                        #no value, first child is expression
                        pass
                elif node.properties["type"] == 'class':
                        #This does not generate code, children of node is code of class
                        for k in node.children:
                                t = translate(k, labelCount, addresses)
                                out += t[0]
                                labelCount = t[1]
                elif node.properties["type"] == 'functionCall':
                        #value of function name, children include the arguments passed to the functionCall
                        out += ("call " + node.properties["name"] + " " + len(node.children) + "\n")
                elif node.properties["type"] == 'subroutine':
                        #value of function name, children is statementList of code
                        out += ("function " + node.properties["name"] + " " + node.properties["localVarCount"] + "\n")
                elif node.properties["type"] == 'operator':
                        #value of whatever operator it is. Children are operand expressions
                         if node.properties["name"] == '+':
                                 out += "add\n"
                         elif node.properties["name"] == '-':
                                 out += "sub\n"
                         elif node.properties["name"] == '*':
                                 out += "call Math.multiply 2\n"
                         elif node.properties["name"] == '/':
                                 out += "call Math.divide 2\n"
                         elif node.properties["name"] == '&':
                                 out += "and\n"
                         elif node.properties["name"] == '|':
                                 out += "or\n"
                         elif node.properties["name"] == '<':
                                 out += "lt\n"
                         elif node.properties["name"] == '>':
                                 out += "gt\n"
                         elif node.properties["name"] == '=':
                                 out += "eq\n"
                                #when used for assignment, handled by letStatement node
                elif node.properties["type"] == "unaryOperator":
                        #value of whatever operator it is. Child is operand expression
                        if node.properties["name"] == '~':
                                out += "not\n"
                        if ndoe.value == '-':
                                out += "neg\n"
                elif node.properties["type"] == 'integerConstant':
                        #value of integer. No children.
                        out += ("push constant " + node.properties["name"] + "\n")
                elif node.properties["type"] == 'StringConstant':
                        #value of string. No children.
                        pass
                elif node.properties["type"] == 'KeywordConstant':
                        #value of keyword (true, false, null, this). No children.
                        pass
                elif node.properties["type"] == 'expression':
                        pass
                elif node.properties["type"] == 'root':
                        #root: no value, children are class nodes
                elif node.properties["type"] == 'statementList':
                        #no value, children are lines of code
                        
def translateRoot(node, addresses):
        print "starts",node.children
        for k in node.children:
                print "first CHILD"
                print(translate(k,0,addresses))
        print "done"



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
        translateRoot(parsed[0], parsed[1])
