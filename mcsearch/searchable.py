
from nbt import nbt

from . import nbt_util

class Searchable:
	def search(self, id = None, name = "", searchBlocks = False, tags = None, keys = None, verbose = 0):
		if(searchBlocks):
			yield from self.search_blocks(id, verbose = verbose)
		else:
			if(not tags):
				tags = []
			if(name != ""):
				tags.append(nbt_util.nameToTAG_Search(name))
			if(id):
				tags.append(nbt_util.idToTAG_Search(id))
			if(not keys):
				keys = ["Entities", "TileEntities"]
			yield from self.search_nbt(tags, keys = keys, verbose = verbose)
	
	def search_nbt(self, tags, keys = None, verbose = 0):
		pass

	def search_blocks(self, id, verbose = 0):
		pass

	def __repr__(self):
		return str(self)
