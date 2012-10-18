class JackParser:

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.className = ''
        self.globalClassAddresses = {}
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
        self.tokenizer.popToken()

    def _pushToken(self):
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
                if nextToken !=  parseObj:
                    raise ('Syntax error')
        return tuple(captures)

    def parseMany(self, startToken, item):
        if ~(self._isFunction(item)):
            raise ('Function not passed to parseMany')
        nextToken = self._popToken()
        if ~(isinstance(startToken, list)):
            startToken = [startToken]
        while (nextToken in startToken):
            self._pushToken()
            yield item()
            nextToken = self._popToken()
        self._pushToken()

    def parseAll(self):
        children = list(self.parseMany(('keyword', 'class'), self.parseClass))
        return (JackExpressionTree({'type': 'root'}, None, children),
                self.addresses,
                self.functionLocalCounts)

    def parseClass(self):
        w, className, w = self.parse([('keyword', 'class'),
            self.parseTokenValue,
            ('symbol', '{')])
        self.className = className
        classBody, w = self.parse([self.parseClassBody,
            ('symbol', '}')])
        self.globalClassAddresses[self.className] = self.addresses[:] #copy
        self.addresses = {} #{'$global' => {}, 'function' => {'exampleVar' => 'static 0'}}
        self.staticCount = 0
        self.statics = {}
        self.instanceVarCount = 0
        self.instanceVars = {}
        self.localVarCounts = {} #function => count
        self.localVars = {} #function => name => type, index
        self.argumentCounts = {} #function => argumentCount
        self.arguments = {} #function => name => type, index
        return JackExpressionTree({'type': 'class', 'name': identifier}, None, classBody.children)

    def parseClassBody(self):
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
        w, statementsTree = self.parse([self.parseVariableDeclarations, self.parseStatements])
        return JackExpressionTree({}, None, statementsTree.children)

    def parseParameterList(self):
        nextToken = self._popToken()
        self._pushToken()
        if nextToken == ('symbol', ')'): return []
        return [self.parseLoneParameter()] + list(self.parseMany(('symbol', ','), self.parseParameter))

    def parseLoneParameter(self):
        w, argType = self.parseTokenValue()
        w, argId = self.parseTokenValue()
        self.localVars[self.functionName][argId] = {}
        self.localVars[self.functionName][argId]['type'] = argType
        self.localVars[self.functionName][argId]['index'] = self.localVarCounts[self.functionName]
        self.addresses[self.functionName][argId] = "argument %s" % (self.localVarCounts[self.functionName])
        self.localVarCounts[self.functionName] += 1
        return argId

    def parseParameter(self):
        w, w = self.parseTokenValue()
        return self.parseLoneParameter()

    def parseVariableDeclarations(self):
        return list(self.parseMany(('keyword', 'var'), self.parseVariableDeclaration))

    def parseVariableDeclaration(self):

    def parseStatements(self):
        children = list(self.parseMany([('keyword', 'do'),
            ('keyword', 'let'),
            ('keyword', 'while'),
            ('keyword', 'return'),
            ('keyword', 'if')],
            self.parseStatement))
        return JackExpressionTree(None, None, children)

    def parseStatement(self):

    def parseDoStatement(self):

    def parseLetStatement(self):

    def parseWhileStatement(self):

    def parseReturnStatement(self):

    def parseIfStatement(self):

    def parseExpression(self):

    def parseExpressionList(self):

    def parseTerm(self):


