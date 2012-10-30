from JackConstants import *

from JackTokenizer import *

from JackParser import *

from JackExpressionTree import *

from JackErrors import *


conditionals = {"=":"eq", "<": "lt", ">": "gt", "&": "and"}


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
                        print node.children[1]
                        self.translate(node.children[1])
                        print "Here is addresses\n"
                        print self.classAddresses
                        identifier = node.children[0].properties['value']
                        if (identifier in self.classAddresses[self.currentClass][self.currentFunction]):
                                self.out += ("pop " + str(self.classAddresses[self.currentClass][self.currentFunction][node.children[0].properties["value"]] + "\n"))
                        else:
                                self.out += ("pop " + str(self.classAddresses[self.currentClass]['$global'][node.children[0].properties["value"]] + "\n"))
                elif node.properties["type"] == "doStatement":
                        for child in node.children:
                                self.translate(child)
                        print node.children[0]
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
                        print "LOLOLOL RETURNINGZ"
                        if len(node.children) != 0:
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
                elif node.properties["type"] == 'binaryOperator':
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
                else:
                        print "FLAGGING THIS THANG! THIS IS A UNKNOWN OPERATOR! FIX ME PLEASE!"
                        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                        print node.properties["type"]



if __name__=="__main__":
        tokenizer = Tokenizer("""
        // This file is part of the materials accompanying the book 
// "The Elements of Computing Systems" by Nisan and Schocken, 
// MIT Press. Book site: www.idc.ac.il/tecs
// File name: projects/09/Square/Square.jack

/**
 * The Square class implements a graphic square. A graphic square 
 * has a location on the screen and a size. It also has methods 
 * for drawing, erasing, moving on the screen, and changing its size.
 */
class Square {

    // Location on the screen
    field int x, y;

    // The size of the square
    field int size;

    /** Constructs a new square with a given location and size. */
    constructor Square new(int Ax, int Ay, int Asize) {
        let x = Ax;
        let y = Ay;
        let size = Asize;

        do draw();

        return this;
    }

    /** Deallocates the object's memory. */
    method void dispose() {
        do Memory.deAlloc(this);
        return;
    }

    /** Draws the square on the screen. */
    method void draw() {
        do Screen.setColor(true);
        do Screen.drawRectangle(x, y, x + size, y + size);
        return;
    }

    /** Erases the square from the screen. */
    method void erase() {
        do Screen.setColor(false);
        do Screen.drawRectangle(x, y, x + size, y + size);
        return;
    }

    /** Increments the size by 2. */
    method void incSize() {
        if (((y + size) < 254) & ((x + size) < 510)) {
            do erase();
            let size = size + 2;
            do draw();
        }
        return;
    }

    /** Decrements the size by 2. */
    method void decSize() {
        if (size > 2) {
            do erase();
            let size = size - 2;
            do draw();
        }
        return;
	}

    /** Moves up by 2. */
    method void moveUp() {
        if (y > 1) {
            do Screen.setColor(false);
            do Screen.drawRectangle(x, (y + size) - 1, x + size, y + size);
            let y = y - 2;
            do Screen.setColor(true);
            do Screen.drawRectangle(x, y, x + size, y + 1);
        }
        return;
    }

    /** Moves down by 2. */
    method void moveDown() {
        if ((y + size) < 254) {
            do Screen.setColor(false);
            do Screen.drawRectangle(x, y, x + size, y + 1);
            let y = y + 2;
            do Screen.setColor(true);
            do Screen.drawRectangle(x, (y + size) - 1, x + size, y + size);
        }
        return;
    }

    /** Moves left by 2. */
    method void moveLeft() {
        if (x > 1) {
            do Screen.setColor(false);
            do Screen.drawRectangle((x + size) - 1, y, x + size, y + size);
            let x = x - 2;
            do Screen.setColor(true);
            do Screen.drawRectangle(x, y, x + 1, y + size);
        }
        return;
    }

    /** Moves right by 2. */
    method void moveRight() {
        if ((x + size) < 510) {
            do Screen.setColor(false);
            do Screen.drawRectangle(x, y, x + 1, y + size);
            let x = x + 2;
            do Screen.setColor(true);
            do Screen.drawRectangle((x + size) - 1, y, x + size, y + size);
        }
        return;
    }
}
""")
        jp = JackParser(tokenizer)
        #print(jp.parseAll()[0])
        parsed = jp.parseAll()
        trans  = translator(parsed[1])
        print("\n\n\nSTARTING ANEW\n\n\n")
        trans.translate(parsed[0])
        trans.output()
        #translateRoot(parsed[0], parsed[1])
