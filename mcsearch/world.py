import glob, os, errno

from . import searchable, region, chunk

class World(searchable.Searchable):
	
	def __init__(self, dir):
		self.path = dir
		if(not os.path.exists(dir)):
			raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), dir)
	
	def search_nbt(self, tags, keys = None, verbose = 0):
		yield from self.__forAllRegions(lambda r: r.search_nbt(tags, keys = keys, verbose = verbose), verbose = verbose)

	def search_blocks(self, id, verbose = 0):
		yield from self.__forAllRegions(lambda r: r.search_blocks(id, verbose = verbose), verbose = verbose)

	def get_region_by_coords(self, x, z):
		rx = x // (32 * 16)
		rz = z // (32 * 16)
		path = os.path.join(self.path, f"r.{rx}.{rz}.mca")
		if(os.path.exists(path)):
			return ((rx * 32 * 16, 0, rz * 32 * 16), region.Region.from_file(path))
		return (None, None)

	def get_chunk_by_coords(self, x, z):
		rx = x // (region.REGION_SIZE)
		rz = z // (region.REGION_SIZE)
		cx = (x - (rx * (region.REGION_SIZE))) // chunk.CHUNK_SIZE
		cz = (z - (rz * (region.REGION_SIZE))) // chunk.CHUNK_SIZE
		path = os.path.join(self.path, f"r.{rx}.{rz}.mca")
		if(os.path.exists(path)):
			return ((rx * region.REGION_SIZE + cx * chunk.CHUNK_SIZE, 0, rz * region.REGION_SIZE + cz * chunk.CHUNK_SIZE), chunk.Chunk.from_region(region.Region.from_file(path), cx, cz))
		return (None, None)

	def __forAllRegions(self, funtion, verbose = 0):
		for path in glob.iglob(os.path.join(self.path, "*.mca")):
			if(verbose > 0):
				print(os.path.basename(path))
			yield from funtion(region.Region.from_file(path))
			if(verbose > 0):
				print("")
	
	def __str__(self):
		return f"<{type(self).__name__}>"