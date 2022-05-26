
class Area:
	def __init__(self, x, z, w, h):
		self.x = x
		self.z = z
		self.w = w
		self.h = h
	
	def getStartPos(self):
		return (self.x, self.z)
	
	def getEndPos(self):
		return (self.x + self.w, self.z + self.h)
