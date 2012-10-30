from JackConstants import *

from JackTokenizer import *

from JackParser import *

from JackExpressionTree import *

from JackErrors import *
"""All Node Types and their properties

ifStatement: no value, first child is expression (must have), second child is statementList for expression true, third child is statementList for else

letStatement: no value, two children, first is variable identifier, second is expression

whileStatement: no value, first child is expression, second child is statementList

returnStatement: no value, first child is expression

functionCall: value of function name, children include the arguments passed to the functionCall

subroutine: value of function name, children include the following code

operator: value of whatever operator it is. Children are operand expressions

unaryOperator: value of whatever operator it is. Child is operand expression

integerConstant: value of integer. No children.

StringConstant: value of string. No children.

KeywordConstant: value of keyword (true, false, null, this). No children.

expression: no value, children are  

root: no value, children are class nodes
"""
def translateRoot(node, addresses):
        print "starts",node.children
        for k in node.children:
                print "first CHILD"
                print(translate(k,0,addresses))
        print "done"

def getProperty(node, addresses, property):
    print node.properties[property]
    cls, prp = node.properties[property].split(".")
    print (cls,prp)
        
def translate(node, labelCount, addresses):
        print ("addresses")
        print (addresses)
        print ("properties")
        print (node.properties)
        print (node.children)
        t = node.properties['name'].split(".")
        print (node.properties['name'])
        classAddresses = addresses[node.properties['name']]
        print(classAddresses)
        out = ""
        if node.properties["type"] == 'ifStatement':
                translate(node.children[0], labelCount)
                out += "not\n"
                out += ("if-goto L" + str(labelCount) + "\n")
                labelCount += 2
                for k in node.children[1:]:
                        t = translate(k, labelCount, addresses)
                        out += t[0]
                        labelCount = t[1]
                out += ("goto L" + str(labelCount - 1) + "\n")
                out += ("label L" + str(labelCount - 2) + "\n")
                #ElseCode
                out += ("label L" + str(labelCount - 1) + "\n")
        elif node.properties["type"] == 'letStatement':
                pass
        elif node.properties["type"] == 'whileStatement':
                out += ("label L" + str(labelCount) + "\n")
                translate(node.children[0], labelCount, addresses)
                out += "not\n"
                out += ("if-goto L" + (labelCount + 1) + "\n")
                for k in node.children[1:]:
                        translate(k, labelCount + 2, addresses)
                out += ("goto L" + labelCount + "\n")
                out += ("label L" + (lableCount + 1) + "\n")
        elif node.properties["type"] == 'returnStatement':
                pass
        elif node.properties["type"] == 'class':
                #This does not generate code, children of node is code of class
                for k in node.children:
                        t = translate(k, labelCount, addresses)
                        out += t[0]
                        labelCount = t[1]
        elif node.properties["type"] == 'functionCall':
                out += ("call " + node.properties["name"] + " " + len(node.children) + "\n")
        elif node.properties["type"] == 'subroutine':
                out += ("function " + node.properties["name"] + " " + node.properties["localVarCount"] + "\n")
        elif node.properties["type"] == 'operator':
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
                if node.properties["name"] == '~':
                        out += "not\n"
                if ndoe.value == '-':
                        out += "neg\n"
        elif node.properties["type"] == 'integerConstant':
                out += ("push constant " + node.properties["name"] + "\n")
        elif node.properties["type"] == 'StringConstant':
                pass
        elif node.properties["type"] == 'KeywordConstant':
                pass
        elif node.properties["type"] == 'expression':
                pass
        return out, labelCount


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
