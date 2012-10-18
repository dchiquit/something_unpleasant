

class JackExpressionTree:

    #properties children, parent
    # properties: {}

    def __init__(self, properties, parent, children = []):
        self.properties, self.parent, self.children = properties, parent, children
        self.parent._addChild(self)
        c.parent = self for c in children

    def _addChild(child):
        self.children += [child]
