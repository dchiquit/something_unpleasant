from JackConstants import *
from JackTokenizer import *
from JackExpressionTree import *
from JackErrors import *

"""

Tokenizer needs an EOF:
("EOF",None)


"""

class JackParser:

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.className = ''
        self.globalClassInfo = {}
        self.addresses = {'$global': {}} #{'$global' => {}, 'function' => {'exampleVar' => 'static 0'}}
        ###private
        self.staticCount = 0
        self.statics = {}
        self.instanceVarCount = 0
        self.instanceVars = {}
        self.localVarCounts = {} #function => count
        self.localVars = {} #function => name => type, index
        self.argumentCounts = {} #function => argumentCount
        self.arguments = {} #function => name => type, index
        self.resolve = {}

    def _popToken(self):
        ret = self.tokenizer.popToken()
        print(ret)
        return ret

    def _pushToken(self):
        self.tokenizer.pushToken()

    def _canPop(self):
        return self.tokenizer.canPop()

    def _isFunction(self, x):
        return hasattr(x, '__call__')

    def parse(self, items):
        captures = []
        if not(isinstance(items, list)):
            items = [items]
        for parseObj in items:
            if self._isFunction(parseObj):
                captures += [parseObj()]
            else:
                nextToken = self._popToken()
                captures += [nextToken]
                if nextToken != parseObj:
                    raise JackParserError("Syntax error while parsing %s" % (items))
        return tuple(captures)

    def parseMany(self, startToken, item):
        if not(self._isFunction(item)):
            raise JackParserError('Function not passed to parseMany')
        nextToken = self._popToken()
        if not(isinstance(startToken, list)):
            startToken = [startToken]
        while (nextToken in startToken):
            self._pushToken()
            yield item()
            nextToken = self._popToken()
        self._pushToken()

    def parseAll(self):
        children = list(self.parseMany(('keyword', 'class'), self.parseClass))
        print('Global info:')
        print(self.globalClassInfo)
        return (Node({'type': 'root'}, None, children),
                self.globalClassInfo)

    def parseClass(self):
        print('Parsing class!')
        self.resolve = {}
        self.resolve['$global'] = {}
        w, className, w = self.parse([('keyword', 'class'),
            self.parseTokenValue,
            ('symbol', '{')])
        self.className = className
        classBody, w = self.parse([self.parseClassBody,
            ('symbol', '}')])
        self.globalClassInfo[self.className] = self.addresses.copy()
        self.addresses = {'$global': {}} #{'$global' => {}, 'function' => {'exampleVar' => 'static 0'}}
        self.staticCount = 0
        self.statics = {}
        self.instanceVarCount = 0
        self.instanceVars = {}
        self.localVarCounts = {} #function => count
        self.localVars = {} #function => name => type, index
        self.argumentCounts = {} #function => argumentCount
        self.arguments = {} #function => name => type, index
        return Node({'type': 'class', 'name': self.className}, None, classBody.children)

    def parseClassBody(self):
        print('Parsing class body!')
        declarations = list(self.parseMany([('keyword', 'static'),
            ('keyword', 'field')],
            self.parseVariableDeclaration))
        subroutines = list(self.parseMany([('keyword', 'function'),
            ('keyword', 'constructor'),
            ('keyword', 'method')],
            self.parseSubroutine))
        return Node({}, None, subroutines)

    def parseTokenValue(self):
        w, idt = self._popToken()
        return idt

    def parseVariableDeclaration(self):
        print('Parsing var dec')
        self.scope, self.varType = self.parse([self.parseTokenValue, self.parseTokenValue])
        names, w = self.parse([self.parseVariableList, ('symbol', ';')])
        print('Exiting var dec')
        print(names)
        return names

    def parseLoneVariable(self):
        print('Parsing lone variable')
        name = self.parseTokenValue()
        if self.scope == 'static':
            self.statics[name] = {}
            self.statics[name]['type'] = self.varType
            self.statics[name]['index'] = self.staticCount
            self.addresses['$global'][name] = "static %s" % (self.statics[name]['index'])
            self.resolve['$global'][name] = self.varType
            self.staticCount += 1
        elif self.scope == 'field':
            self.instanceVars[name] = {}
            self.instanceVars[name]['type'] = self.varType
            self.instanceVars[name]['index'] = self.instanceVarCount
            self.addresses['$global'][name] = "this %s" % (self.instanceVars[name]['index'])
            self.resolve['$global'][name] = self.varType
            self.instanceVarCount += 1
        elif self.scope == 'var':#fill this in
            self.localVars[self.functionName][name] = {}
            self.localVars[self.functionName][name]['type'] = self.varType
            self.localVars[self.functionName][name]['index'] = self.localVarCounts[self.functionName]
            self.addresses[self.functionName][name] = "local %s" % (self.localVars[self.functionName][name]['index'])
            self.resolve[self.functionName][name] = self.varType
            self.localVarCounts[self.functionName] += 1
        else:
            raise JackParserError('Invalid scope')
        return name

    def parseVariable(self):
        print('Parsing variable')
        self.parseTokenValue()
        return self.parseLoneVariable()

    def parseVariableList(self):
        print('Parsing variable list')
        return [self.parseLoneVariable()] + list(self.parseMany(('symbol', ','), self.parseVariable))

    def parseSubroutine(self):
        print('Parsing subroutine')
        methodType, returnType, name = self.parse([self.parseTokenValue,
            self.parseTokenValue,
            self.parseTokenValue])
        self.functionName = name
        self.addresses[name] = {}
        self.localVars[name] = {}
        self.arguments[name] = {}
        self.argumentCounts[name] = 0
        self.localVarCounts[name] = 0
        self.resolve[name] = {}
        w, parameterList, w, body = self.parse([('symbol', '('),
            self.parseParameterList,
            ('symbol', ')'),
            self.parseSubroutineBody])
        print('Exiting subroutine header')
        print(parameterList)
        return Node({'type': 'subroutine', 
            'name': "%s.%s" % (self.className, self.functionName),
            'localVarCount': self.localVarCounts[name],
            'returnType': returnType,
            'functionType': methodType},
            None, body.children)

    def parseSubroutineBody(self):
        print('Parsing subroutine body')
        w, w, statementsTree, w = self.parse([('symbol', '{'),
            self.parseVariableDeclarations, 
            self.parseStatements,
            ('symbol', '}')])
        return Node({}, None, statementsTree.children)

    def parseParameterList(self):
        print('Parsing parameter list')
        nextToken = self._popToken()
        self._pushToken()
        if nextToken == ('symbol', ')'): return []
        return [self.parseLoneParameter()] + list(self.parseMany(('symbol', ','), self.parseParameter))

    def parseLoneParameter(self):
        print('Parsing lone parameter')
        argType = self.parseTokenValue()
        argId = self.parseTokenValue()
        self.arguments[self.functionName][argId] = {}
        self.arguments[self.functionName][argId]['type'] = argType
        self.arguments[self.functionName][argId]['index'] = self.argumentCounts[self.functionName]
        self.addresses[self.functionName][argId] = "argument %s" % (self.argumentCounts[self.functionName])
        self.resolve[self.functionName][argId] = argType
        self.argumentCounts[self.functionName] += 1
        return argId

    def parseParameter(self):
        print('Parsing parameter')
        self.parseTokenValue()
        return self.parseLoneParameter()

    def parseVariableDeclarations(self):
        print('Parsing vardec')
        return list(self.parseMany(('keyword', 'var'), self.parseVariableDeclaration))

    def parseStatements(self):
        print('Parsing statements')
        children = list(self.parseMany([('keyword', 'do'),
            ('keyword', 'let'),
            ('keyword', 'while'),
            ('keyword', 'return'),
            ('keyword', 'if')],
            self.parseStatement))
        print('Done parsing statement block')
        return Node({}, None, children)

    def parseStatement(self):
        nextToken = self._popToken()
        self._pushToken()
        if nextToken == ('keyword', 'let'):
            return self.parseLetStatement()
        elif nextToken == ('keyword', 'do'):
            return self.parseDoStatement()
        elif nextToken == ('keyword', 'if'):
            return self.parseIfStatement()
        elif nextToken == ('keyword', 'return'):
            return self.parseReturnStatement()
        elif nextToken == ('keyword', 'while'):
            return self.parseWhileStatement()

    def parseDoStatement(self):
        w, ret, w = self.parse([('keyword', 'do'), self.parseSubroutineCall, ('symbol', ';')])
        return Node({'type': 'doStatement'}, None, [ret])

    def parseSubroutineCall(self):
        ident1, next = self.parseTokenValue(), self.parseTokenValue()
        if next == '(':
            argList, w = self.parse([self.parseArgumentList, ('symbol', ')')])
            return Node({'type': 'functionCall', 'value': "%s.%s" % (self.className, ident1)}, None,
                [Node({'type': 'this'}, None, [])] + argList)
        elif next == '.':
            ident2, w, argList, w = self.parse([self.parseTokenValue, ('symbol', '('), self.parseArgumentList, ('symbol', ')')])
            if ident1 in self.resolve[self.functionName].keys():
                varType = self.resolve[self.functionName][ident1]
                return Node({'type': 'functionCall', 'value': "%s.%s" % (varType, ident2)}, None,
                    [Node({'type': 'identifier', 'value': ident1}, None, [])] + argList)
            elif ident1 in self.resolve['$global'].keys():
                varType = self.resolve['$global'][ident1]
                return Node({'type': 'functionCall', 'value': "%s.%s" % (varType, ident2)}, None,
                    [Node({'type': 'identifier', 'value': ident1}, None, [])] + argList)
            else:
                return Node({'type': 'functionCall', 'value': "%s.%s" % (ident1, ident2)}, None, argList)
        else:
            raise JackParserError('Expected ( or . next.')

    def parseArgumentList(self):
        nextToken = self.parseTokenValue()
        self._pushToken()
        if nextToken == ')':
            return []
        exps = [self.parseExpression()]
        exps += list(self.parseMany(('symbol', ','), self.parseExpressionWithComma))
        return exps

    def parseLetStatement(self):
        print('Parsing let statement')
        w, leftExpression, w, rightExpression, w = self.parse([('keyword', 'let'), self.parseLHS, ('symbol', '='), self.parseRHS, ('symbol', ';')])
        return Node({'type': 'let', 'array': leftExpression.properties['value'] == '['},
            None, [leftExpression, rightExpression])

    def parseLHS(self):
        print('Parsing LHS')
        identifier, bracketOperator = self.parse([self.parseTokenValue, self.parseTokenValue])
        if bracketOperator == '[':
            indexTree = self.parseExpression()
            self.parse(('symbol', ']'))
            return Node({'type': 'operator', 'value': '['}, None,
                [Node({'type': 'identifier', 'value': identifier}, None, []), indexTree])
        else:
            self._pushToken()
            return Node({'type': 'identifier', 'value': identifier}, None, [])

    def parseRHS(self):
        print('Parsing RHS')
        nextToken = self._popToken()
        if nextToken == ('keyword', 'new'):
            print('Parsing constructor')
            classIdentifier = self.parseTokenValue()
            self._pushToken()
            ctorCall = self.parseExpression()
            ctorCall.children = ctorCall.children[1:]
            ctorCall.properties['value'] = ("%s.new" % (classIdentifier))
            return ctorCall
        else:
            self._pushToken()
            return self.parseExpression()

    def parseWhileStatement(self):
        print('Parsing while statement')
        w, w, conditional, w, w, statementList, w = self.parse([('keyword', 'while'),
            ('symbol', '('),
            self.parseExpression,
            ('symbol', ')'),
            ('symbol', '{'),
            self.parseStatements,
            ('symbol', '}')])
        statementList.properties['type'] = 'statementList'
        conditional.properties['type'] = 'conditional'
        return Node({'type': 'whileStatement'}, None, [conditional, statementList])

    def parseReturnStatement(self):
        print('Parsing return statement')
        w, ret, w = self.parse([('keyword', 'return'), self.parseExpression, ('symbol', ';')])
        return Node({'type': 'returnStatement'}, None, [ret])

    def parseIfStatement(self):
        print('Parsing if statement')
        w, w, conditional, w, w, statementList, w = self.parse([('keyword', 'if'),
            ('symbol', '('),
            self.parseExpression,
            ('symbol', ')'),
            ('symbol', '{'),
            self.parseStatements,
            ('symbol', '}')])
        conditional.properties['type'] = 'conditional'
        statementList.properties['type'] = 'statementList'
        nextToken = self._popToken()
        self._pushToken()
        if nextToken == ('keyword', 'else'):
            elseStatementList = self.parseElseStatement()
            elseStatementList.properties['type'] = 'statementList'
            return Node({'type': 'ifStatementWithElse'}, None, [conditional, statementList, elseStatementList])
        return Node({'type': 'ifStatement'}, None, [conditional, statementList])

    def parseElseStatement(self):
        print('Parsing else statement')
        w, w, statementList, w = self.parse([('keyword', 'else'), ('symbol', '{'), self.parseStatements, ('symbol', '}')])
        return statementList

    def parseExpressionWithComma(self):
        w, exp = self.parse([('symbol', ','), self.parseExpression])
        return exp

    def parseExpression(self): #stops at ',' , ')' , ']', ';'
        print('Parsing expression')
        tree = self.parseLoneTerm()
        for term in self.parseMany(operators, self.parseTerm):
            op, opand = term
            tree = Node({'type': 'binaryOperator', 'value': op}, None, [tree, opand])
        return tree

    def parseTerm(self):
        print('Parsing term')
        op, term = self.parse([self.parseTokenValue, self.parseLoneTerm])
        print((op, term))
        return (op, term)

    def parseLoneTerm(self):
        print('Parsing lone term')
        tokenType, tokenValue = self._popToken()
        if (tokenType == 'integerConstant') or (tokenType == 'stringConstant') or (tokenType == 'keywordConstant'):
            return Node({'type': tokenType, 'value': tokenValue}, None, [])
        elif tokenType == 'identifier':
            ahead = self.parseTokenValue()
            self._pushToken()
            if ahead == '.':
                self._pushToken()
                return self.parseSubroutineCall()
            elif ahead == '[':
                inside = self.parseExpression()
                w = self.parse(('symbol', ']'))
                return Node({'type': 'operator', 'value': '['}, None,
                    [Node({'type': 'identifier', 'value': tokenValue}, None, []), inside])
            elif ahead == '(':
                self._pushToken()
                return self.parseSubroutineCall()
            else:
                return Node({'type': 'identifier', 'value': tokenValue}, None, [])
        elif tokenType == 'symbol' and tokenValue == '(':
            expTree, w = self.parse([self.parseExpression, ('symbol', ')')])
            return expTree
        elif tokenType == 'symbol':
            return Node({'type': 'unaryOperator', 'value': tokenValue}, None, [self.parseLoneTerm()])
        else:
            raise JackParserError('Invalid term start')

if __name__ == "__main__":
    tokenizer = Tokenizer("""
    class Wassup {
        field int test, test3, test4, test5;
        field int test2;
        static int test421;

        method int testanotherthing(int a, String b) {
            var int fs, h;
            var int g;
            var String b;
            var Troll c;
            let fs = 123 + 123 + (123 - 123 * 123);
            let g = (fs + 3) / 91;
            let b = "blah" + "blah";
            let fs = c.trollmethod(123, 123, 123*123*c.trollmethod(10110));
            let fs = new Troll(123, trolll());
            if (fs) {
                do Troll.trollmethod(123, 123, 123);
                let fs = 0;
            }
            while (fs) {
                do Troll.trollmethod(123, 123, 456);
                return fs;
            }
            return fs;
        }
    }""")
    jp = JackParser(tokenizer)
    print(jp.parseAll()[0])
