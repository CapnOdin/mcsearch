
import mcsearch

from functools import reduce
import operator

class TagsCategoryNotFoundInChunk(Exception):
	def __init__(self, keys, chunk, cause, verbose = 0):
		self.keys = keys
		self.chunk = chunk
		self.cause = cause
		self.verbose = verbose

	def getLookupPath(self):
		return f"{self.chunk}.data{('.' + '.'.join(self.keys) if self.keys else '')}"

	def __str__(self):
		string = f"Cannot find '{self.cause}' in '{self.getLookupPath()}'"
		if(self.verbose >= mcsearch.VERBOSE_TAGS):
			string += "\n" + f"{reduce(operator.getitem, self.keys, self.chunk.data).pretty_tree()}"

		return string

class DimentionNotInWorldDir(Exception):
	pass

class CoordsNotInArea(Exception):
	def __init__(self, coords, area, verbose = 0):
		self.coords = coords
		self.area = area
		self.verbose = verbose
	
	def __str__(self):
		bound1 = self.area.getStartPos()
		bound2 = self.area.getEndPos()
		return f"Coordinates ({', '.join(map(str, self.coords))}) are not within {self.area}. The following should hold {bound1[0]} <= {self.coords[0]} <= {bound2[0]} and {bound1[1]} <= {self.coords[1]} <= {bound2[1]}"
