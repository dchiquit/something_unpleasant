# Teh comment

"""

class Node:
        [] children
        Node parent
        "" value
        "" type

class Parser:
        {} class_variables
        {} static_variables
        {} function_arguments
        {} function_locals
        ^one of these would have type, index (number)

"""

import JackConstants, JackErrors

class Tokenizer:

    def __init__(self, file):
        self.file = file
                self.tokens = []
                self._preprocess()
                self.file = self.file.replace("\n"," ").replace("\t"," ")
                print(self.file)

        def _preprocess(self):
            pass

        def _matchesToken(self, token, strang):
            return len(token) >= len(strang) and token[:len(strang)] == strang

        def _read(self):
            if not self.canPop(): raise JackErrors.JackParserError("Nothing to read")
                ret = ""
                for i in range(0,len(self.file)):
                    if self.file[i] != " ":
                        ret += self.file[i]
                    else:
                        return ret
                return ret

        def _pop(self, type, token):
            self.file = self.file[len(token):]
                self.tokens = [(type, token)] + self.tokens
                return (type, token)

        def popToken(self):
            self.file = self.file.strip()
                token = self._read()
                for key in JackConstants.keyword:
                    if self._matchesToken(token, key):
                        return self._pop("keyword", key)
                for symbol in JackConstants.symbol:
                    if self._matchesToken(token, symbol):
                        return self._pop("keyword", symbol)
                if self.file[0] == '"':
                    for i in range(1,len(self.file)):
                        if self.file[i] == '"':
                            return self._pop("stringConstant", self.file[:i+1])
                        raise JackErrors.JackParserError("No string terminator")
                nums = "0123456789"
                if token[0] in nums:
                    for i in range(1,len(self.file)):
                        if self.file[i] not in nums:
                            t = int(self.file[:i])
                                        if t > 32767:
                                            raise JackErrors.JackParserError("Integer constant "+self.file[:i]+" is too large")
                                        return self._pop("integerConstant", str(t))
                        raise JackErrors.JackParserError("Nothing after integer constant "+self.file)
                if token[0].isalpha() or self.file[0] == "_":
                    ret = ""
                        while len(token) > 0:
                            if token[0].isalpha() or token[0].isdigit() or token[0] == "_":
                                ret += token[0]
                                        token = token[1:]
                                else:
                                    return self._pop("identifier",ret)
                        return self._pop("identifier", ret)
                    #raise JackErrors.JackParserError("Nothing after identifier "+ret)
                raise JackErrors.JackParserError("No token found")
        def pushToken(self):
            self.file = self.tokens[0][1] + self.file
                self.tokens = self.tokens[1:]

        def canPop(self):
            return not (self.file.isspace() or self.file == "")

if __name__ == "__main__":
    tokenizer = Tokenizer("""
        class   Yo  {
                method Fraction foo (int y) {
                        let temp = (xxx+12)*-63;
                }
        }
""")
    while tokenizer.canPop():
        print tokenizer.popToken()



