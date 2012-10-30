from JackConstants import *
from JackTokenizer import *
from JackExpressionTree import *

"""

Tokenizer needs an EOF:
("EOF",None)


"""

class JackParser:

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.className = ''
        self.globalClassInfo = {}
        self.addresses = {} #{'$global' => {}, 'function' => {'exampleVar' => 'static 0'}}
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
        for parseObj in items:
            if self._isFunction(parseObj):
                captures += [parseObj()]
            else:
                nextToken = self._popToken()
                captures += [nextToken]
                if nextToken != parseObj:
                    raise Exception('Syntax error')
        return tuple(captures)

    def parseMany(self, startToken, item):
        if not(self._isFunction(item)):
            raise Exception('Function not passed to parseMany')
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
        return (JackExpressionTree({'type': 'root'}, None, children),
                self.globalClassInfo)

    def parseClass(self):
        print('Parsing class!')
        w, className, w = self.parse([('keyword', 'class'),
            self.parseTokenValue,
            ('symbol', '{')])
        self.className = className
        classBody, w = self.parse([self.parseClassBody,
            ('symbol', '}')])
        self.globalClassInfo[self.className] = { 'addresses': self.addresses.copy(), 'functionLocalCounts': self.localVarCounts.copy() }
        self.addresses = {} #{'$global' => {}, 'function' => {'exampleVar' => 'static 0'}}
        self.staticCount = 0
        self.statics = {}
        self.instanceVarCount = 0
        self.instanceVars = {}
        self.localVarCounts = {} #function => count
        self.localVars = {} #function => name => type, index
        self.argumentCounts = {} #function => argumentCount
        self.arguments = {} #function => name => type, index
        return JackExpressionTree({'type': 'class', 'name': self.className}, None, classBody.children)

    def parseClassBody(self):
        print('Parsing class body!')
        declarations = list(self.parseMany([('keyword', 'static'),
            ('keyword', 'field')],
            self.parseClassVariableDeclaration))
        subroutines = list(self.parseMany([('keyword', 'function'),
            ('keyword', 'constructor'),
            ('keyword', 'method')],
            self.parseSubroutine))
        return JackExpressionTree({}, None, subroutines)

    def parseTokenValue(self):
        w, idt = self._popToken()
        return idt

    def parseClassVariableDeclaration(self):
        print('Parsing class instance var dec')
        scope, varType, name, w = self.parse([self.parseTokenValue,
            self.parseTokenValue,
            self.parseTokenValue,
            ('keyword', ';')])
        if scope == 'static':
            self.statics[name] = {}
            self.statics[name]['type'] = varType
            self.statics[name]['index'] = self.staticCount
            self.addresses['$global'][name] = "static %s" % (self.statics[name]['index'])
            self.staticCount += 1
        elif scope == 'field':
            self.instanceVars[name] = {}
            self.instanceVars[name]['type'] = varType
            self.instanceVars[name]['index'] = self.instanceVarCount
            self.addresses['$global'][name] = "this %s" % (self.instaceVars[name]['index'])
            self.instanceVarCount += 1
        return name

    def parseSubroutine(self):
        print('Parsing subroutine')
        methodType, returnType, name = self.parse([self.parseTokenValue,
            self.parseTokenValue,
            self.parseTokenValue])
        self.functionName = name
        self.functionLocalCounts[name] = 0
        w, w, w, body = self.parse([('symbol', '('),
            self.parseParameterList,
            ('symbol', ')'),
            self.parseSubroutineBody])
        return JackExpressionTree({'name': "%s.%s" % (self.className, self.functionName),
            'returnType': returnType},
            None, body.children)

    def parseSubroutineBody(self):
        print('Parsing subroutine body')
        w, statementsTree = self.parse([self.parseVariableDeclarations, self.parseStatements])
        return JackExpressionTree({}, None, statementsTree.children)

    def parseParameterList(self):
        print('Parsing parameter list')
        nextToken = self._popToken()
        self._pushToken()
        if nextToken == ('symbol', ')'): return []
        return [self.parseLoneParameter()] + list(self.parseMany(('symbol', ','), self.parseParameter))

    def parseLoneParameter(self):
        print('Parsing lone parameter')
        w, argType = self.parseTokenValue()
        w, argId = self.parseTokenValue()
        self.localVars[self.functionName][argId] = {}
        self.localVars[self.functionName][argId]['type'] = argType
        self.localVars[self.functionName][argId]['index'] = self.localVarCounts[self.functionName]
        self.addresses[self.functionName][argId] = "argument %s" % (self.localVarCounts[self.functionName])
        self.localVarCounts[self.functionName] += 1
        return argId

    def parseParameter(self):
        print('Parsing parameter')
        w, w = self.parseTokenValue()
        return self.parseLoneParameter()

    def parseVariableDeclarations(self):
        print('Parsing vardec')
        return list(self.parseMany(('keyword', 'var'), self.parseVariableDeclaration))

    def parseVariableDeclaration(self):
        pass
        
    def parseStatements(self):
        print('Parsing statements')
        children = list(self.parseMany([('keyword', 'do'),
            ('keyword', 'let'),
            ('keyword', 'while'),
            ('keyword', 'return'),
            ('keyword', 'if')],
            self.parseStatement))
        return JackExpressionTree(None, None, children)

    def parseStatement(self):
        pass

    def parseDoStatement(self):
        pass

    def parseLetStatement(self):
        pass

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
        field int yo;
    }""")
    jp = JackParser(tokenizer)
    print(jp.parseAll()[0])
