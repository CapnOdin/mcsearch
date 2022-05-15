import anvil

from nbt import nbt

from . import searchable, chunk, constants

REGION_SIZE_IN_CHUNKS = 32

REGION_SIZE = REGION_SIZE_IN_CHUNKS * chunk.CHUNK_SIZE

class Region(searchable.Searchable, anvil.Region):
	def search_nbt(self, tags, keys = None, verbose = 0):
		yield from self.__forAllChunks(lambda c: c.search_nbt(tags, keys = keys, verbose = verbose), verbose = verbose)

	def search_blocks(self, id, verbose = 0):
		yield from self.__forAllChunks(lambda c: c.search_blocks(id, verbose = verbose), verbose = verbose)
	
	def __forAllChunks(self, funtion, verbose = 0):
		aChunk = None
		for i in range(REGION_SIZE_IN_CHUNKS):
			for j in range(REGION_SIZE_IN_CHUNKS):
				try:
					aChunk = chunk.Chunk.from_region(self, i, j)
				except (anvil.errors.ChunkNotFound, IndexError) as e:
					if(verbose >= constants.VERBOSE_ERRORS):
						print(e)
					continue
				try:
					for res in funtion(aChunk):
						yield res
				except Exception as e:
					if(verbose >= constants.VERBOSE_ERRORS):
						print(e)
					raise e
	
	def __str__(self):
		offx = self.data["xPos"].value * REGION_SIZE
		offz = self.data["zPos"].value * REGION_SIZE
		return f"<{type(self).__name__} at ({offx}, {offz})>"
	