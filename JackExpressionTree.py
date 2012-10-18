

class JackExpressionTree:

	#properties children, parent
	# properties: {}
	
	def __init__(self, properties, value, parent):
		self.properties = properties
		self.parent = parent
		self.children = []
		self.parent._addChild(self)
	
	def _addChild(child):
		self.children += [child]
	