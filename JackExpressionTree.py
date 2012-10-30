

class Node:

    #properties children, parent
    # properties: {}
    
    # self.properties = {}
    # self.parent = Node
    # self.children = [Node]

    def __init__(self, properties, parent, children = []):
        self.properties, self.parent, self.children = properties, parent, children
        #self.parent._addChild(self)
        for c in children:
            c.parent = self
        
    def __str__(self, tabs=""):
        ret = tabs+str(self.properties)+"\n"
        for c in self.children:
            ret += str(c)+tabs+"\t"
        return ret
            
    def addChild(self, child):
        pass

        
if __name__ == "__main__":
    print(dir(Node))
