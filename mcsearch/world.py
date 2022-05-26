import glob, os, errno

from . import searchable, region, chunk, constants

class World(searchable.Searchable):
	
	def __init__(self, dir):
		self.path = dir
		if(not os.path.exists(dir)):
			raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), dir)
	
	def search_nbt(self, tags, keys = None, verbose = 0):
		yield from self._forAllRegions(lambda r: r.search_nbt(tags, keys = keys, verbose = verbose), verbose = verbose)

	def search_blocks(self, id, verbose = 0):
		yield from self._forAllRegions(lambda r: r.search_blocks(id, verbose = verbose), verbose = verbose)

	def get_region_by_coords(self, x, z):
		path = os.path.join(self.path, region.Region._coordsToFilename(x, z))
		if(os.path.exists(path)):
			r = region.Region.from_file(path)
			return ((r.x, 0, r.z), r)
		return (None, None)

	def get_chunk_by_coords(self, x, z):
		pos, r = self.get_region_by_coords(x, z)
		if(r):
			c = r.chunkByCoords(x, z)
			return ((c.x, 0, c.z), c)
		return (None, None)

	def _forAllRegions(self, funtion, verbose = 0):
		for path in glob.iglob(os.path.join(self.path, "*.mca")):
			if(verbose >= constants.VERBOSE_HIGH):
				print(os.path.basename(path))
			yield from funtion(region.Region.from_file(path))
			if(verbose >= constants.VERBOSE_HIGH):
				print("")
	
	def __str__(self):
		return f"<{type(self).__name__}>"