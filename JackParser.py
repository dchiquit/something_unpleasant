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

    def _popToken(self):
        ret = self.tokenizer.popToken()
        print(ret)
        return ret

    def _pushToken(self):
        print("Pushing token")
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
                    raise JackParserError('Syntax error')
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
        print('Parsing all!')
        children = list(self.parseMany(('keyword', 'class'), self.parseClass))
        print('Global info:')
        print(self.globalClassInfo)
        return (Node({'type': 'root'}, None, children),
                self.globalClassInfo)

    def parseClass(self):
        print('Parsing class!')
        w, className, w = self.parse([('keyword', 'class'),
            self.parseTokenValue,
            ('symbol', '{')])
        self.className = className
        classBody, w = self.parse([self.parseClassBody,
            ('symbol', '}')])
        self.globalClassInfo[self.className] = { 'addresses': self.addresses.copy() }
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
            self.staticCount += 1
        elif self.scope == 'field':
            self.instanceVars[name] = {}
            self.instanceVars[name]['type'] = self.varType
            self.instanceVars[name]['index'] = self.instanceVarCount
            self.addresses['$global'][name] = "this %s" % (self.instanceVars[name]['index'])
            self.instanceVarCount += 1
        elif self.scope == 'var':#fill this in
            self.localVars[self.functionName][name] = {}
            self.localVars[self.functionName][name]['type'] = self.varType
            self.localVars[self.functionName][name]['index'] = self.localVarCounts[self.functionName]
            self.addresses[self.functionName][name] = "local %s" % (self.localVars[self.functionName][name]['index'])
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
        return Node(None, None, children)

    def parseStatement(self):
        nextToken = self._popToken()
        if nextToken == ('keyword', 'let'):
            return self.parseLetStatement()
        if nextToken == ('keyword', 'aofioeafimofmoim'):
            pass
        
    def parseDoStatement(self):
        pass

    def parseLetStatement(self):
        leftExpression, w, rightExpression, ww = self.parse([self.parseLHS, ('symbol', '='), self.parseRHS, ('symbol', ';')])
        print "afaffdsaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa    \t\t",leftExpression, w, rightExpression
        return Node(properties={'type': 'if', 'array': leftExpression.properties['value'] == '['}, 
            None, [leftExpression, rightExpression])
        
    def parseLHS(self):
        return self._popToken()
    
    def parseRHS(self):
        return self._popToken()
        
    def parseWhileStatement(self):
        pass

    def parseReturnStatement(self):
        pass

    def parseIfStatement(self):
        pass

    def parseExpression(self):
        pass

    def parseExpressionList(self):
        pass

    def parseTerm(self):
        pass

if __name__ == "__main__":
    tokenizer = Tokenizer("""
    class Wassup {
        field int test, test3, test4, test5;
        field int test2;
        static int test421;
        
        method int testanotherthing(int a, String b) {
            var int fs;
            let fs = 123;
        }
    }""")
    jp = JackParser(tokenizer)
    print(jp.parseAll()[0])
