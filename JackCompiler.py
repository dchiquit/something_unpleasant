from JackConstants import *

from JackTokenizer import *

from JackParser import *

from JackExpressionTree import *

from JackErrors import *


conditionals = {"=":"eq", "<": "lt", ">": "gt"}


class translator:
        def __init__(self, _classAddresses):
                self.labelCount = 0
                self.out = ""
                self.currentClass = ""
                self.currentFunction = ""
                self.classAddresses = _classAddresses
        def output(self):
                print "Here is out"
                print "<"
                print str(self.out)
                print ">"
        def translate(self, node):
                print  "\n\nTRANSLATING\n\n"
                print (str(node.properties) + "\t" + str(node.children) +"\n")
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
                elif node.properties["type"] == 'let':
                        #no value, two children, first is variable identifier, second is expression
                        #assuming type is integer
                        print node.children[1]
                        self.out += ("push constant " + str(node.children[1].properties["value"]) + "\n")
                        print "Here is addresses\n"
                        print self.classAddresses
                        identifier = node.children[0].properties['value']
                        if (identifier in self.classAddresses[self.currentClass][self.currentFunction]):
                                self.out += ("pop " + str(self.classAddresses[self.currentClass][self.currentFunction][node.children[0].properties["value"]] + "\n"))
                        else:
                                self.out += ("pop " + str(self.classAddresses[self.currentClass]['$global'][node.children[0].properties["value"]] + "\n"))
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
                        print "LOLOLOL RETURNINGZ"
                        identifier = node.children[0].properties['value']
                        if (identifier in self.classAddresses[self.currentClass][self.currentFunction]):
                                self.out += ("push " + str(self.classAddresses[self.currentClass][self.currentFunction][node.children[0].properties["value"]] + "\n"))
                        elif (identifier in self.classAddresses[self.currentClass]['$global']):
                                self.out += ("push " + str(self.classAddresses[self.currentClass]['$global'][node.children[0].properties["value"]] + "\n"))
                        self.out += "return\n"
                elif node.properties["type"] == 'class':
                        #This does not generate code, children of node is code of class
                        self.currentClass = node.properties['name']
                        for k in node.children:
                                self.translate(k)
                elif node.properties["type"] == 'functionCall':
                        #value of function name, children include the arguments passed to the functionCall
                        print "functioning"
                        print node.properties
                        for k in node.children:
                                print k
                                print "translating"
                                self.translate(k)
                                print "done translating"
                        self.out += ("call " + node.properties["value"] + " " + str(len(node.children)) + "\n")
                        print "done functioning"
                elif node.properties["type"] == 'subroutine':
                        #value of function name, children is statementList of code
                        self.currentFunction = node.properties['name']
                        self.out += ("function " + self.currentClass+"."+node.properties["name"] + " " + str(node.properties["localVarCount"]) + "\n")
                        print node.children[0]
                        for k in node.children:
                                self.translate(k)
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
                elif node.properties["type"] == 'KeywordConstant':
                        #value of keyword (true, false, null, this). No children.
                        if node.properties['name'] == 'true':
                                self.out += "push constant 1\n"
                        if node.properties['name'] == 'false':
                                self.out += "push constant 0\n"
                        if node.properties['name'] == 'null':
                                self.out += "push constant 0\n"
                        if node.properties['name'] == 'this':
                                pass
                elif node.properties["type"] == 'conditional':
                        print node.properties
                        print "conditionaling"
                        self.translate(node.children[0])
                        self.translate(node.children[1])
                        self.out += conditionals[node.properties["value"]]+"\n"
                        pass
                elif node.properties["type"] == 'root':
                        #root: no value, children are class nodes
                        for k in node.children:
                                self.translate(k)
                elif node.properties["type"] == 'statementList':
                        #no value, children are lines of code
                        for k in node.children:
                                self.translate(k)



if __name__=="__main__":
        tokenizer = Tokenizer("""
        class Wassup {
        field int test, test3, test4, test5;
        field int test2;
        static int test421;

        method int giveback(int a){
                return a;
                }
                
        method int testanotherthing(int a, String b) {
            var int fs;
            var String f;
            if (giveback(1) = Lol.giveback(1)) {
                    let fs = 42;
                    let f = "Lawl";
                    }
            else {
                    let fs = 21;
                    let f = "No";
                    }
            return fs;
        }
        }""")
        jp = JackParser(tokenizer)
        #print(jp.parseAll()[0])
        parsed = jp.parseAll()
        trans  = translator(parsed[1])
        print("\n\n\nSTARTING ANEW\n\n\n")
        trans.translate(parsed[0])
        trans.output()
        #translateRoot(parsed[0], parsed[1])
