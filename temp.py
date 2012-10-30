
import JackParser, JackTokenizer

class JackParserr(JackParser.JackParser):
    def __init__(self, tokenizer):
        self.ind = 0
        self.tokenizer = tokenizer
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
        self.tokkens = [("integerConstant","7"), ("symbol","+"), ("integerConstant","8")]
    def _popToken(self):
        ret = self.tokkens[self.ind]
        self.ind += 1
        return ret
    def _pushToken(self):
        self.ind -= 1
    def parseTerm(self):
        token = self._popToken()
        print("parsing term ",token)


if __name__ == "__main__":
    t = JackTokenizer.Tokenizer("""
    class Yo {
        method wassup () {
            int x = 123+4;
        }
    }""")
    jp = JackParserr(t)
    print(jp.parseTerm()[0])