

class JackExpressionTree:

    #properties children, parent
    # properties: {}
    
    # self.properties = {}
    # self.parent = JackExpressionTree
    # self.children = [JackExpressionTree]

    def __init__(self, properties, parent, children = []):
        self.properties, self.parent, self.children = properties, parent, children
        #self.parent._addChild(self)
        for c in children:
            c.parent = self
        
    def strang(self, tabs=""):
        ret = tabs+str(self.properties)
        for c in self.children:
            ret += c.strang(tabs+"\t")
        return ret
            
    def addChild(self, child):
        pass

        
if __name__ == "__main__":
    print(dir(JackExpressionTree))
