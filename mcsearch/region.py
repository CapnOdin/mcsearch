import anvil

from . import searchable, chunk, constants, errors, area

import pebble
#import concurrent.futures
import time, dill, platform, os
#import signal, psutil, os

#_DEFAULT_PROCESS_POOL = concurrent.futures.ProcessPoolExecutor()
_DEFAULT_PROCESS_POOL = pebble.ProcessPool()

REGION_SIZE_IN_CHUNKS = 32

REGION_SIZE = REGION_SIZE_IN_CHUNKS * chunk.CHUNK_SIZE

def _searchChunksTread(path, i, function, inclusionCheck = None, verbose = 0):
	lst = []
	try:
		#print(f"Thread {i} start")
		r = Region.from_file(path, inclusionCheck = dill.loads(inclusionCheck))
		lst = list(r._forAllChunks(dill.loads(function), range1 = range(i, i + 1), verbose = verbose))
		#print(f"Thread {i} done")
	except Exception as e:
		print(e)
	return lst

class Region(searchable.Searchable, anvil.Region, area.Area):
	def __init__(self, data: bytes, path = "", x = None, z = None, inclusionCheck = None):
		super().__init__(data)
		self._init(path = path, x = x, z = z, inclusionCheck = inclusionCheck)

	@classmethod
	def from_file(cls, path, x = None, z = None, inclusionCheck = None):
		r = super(Region, cls).from_file(path)
		r._init(path = path, x = x, z = z, inclusionCheck = inclusionCheck)
		return r

	def _init(self, path = "", x = None, z = None, inclusionCheck = None):
		if((x == None or z == None) and path):
			x, z = Region._regionIndexToCoords(*Region._getCoordsFromPath(path))
		if(x != None and z != None):
			area.Area.__init__(self, x, z, REGION_SIZE, REGION_SIZE)
		self.inclusionCheck = inclusionCheck
		self.path = path
	
	def chunkByIndex(self, i, j):
		return chunk.Chunk.from_region(self, i, j)

	def chunkByCoords(self, x, z):
		return self.chunkByIndex(*self._coordsToChunkIndex(x, z))

	def search_nbt(self, tags, keys = None, verbose = 0):
		if(platform.python_implementation() == "PyPy"):
			yield from self._forAllChunks(lambda c: c.search_nbt(tags, keys = keys, verbose = verbose), verbose = verbose)
		else:
			yield from self._forAllChunksThreaded(lambda c: c.search_nbt(tags, keys = keys, verbose = verbose), verbose = verbose)

	def search_blocks(self, id, verbose = 0):
		yield from self._forAllChunksThreaded(lambda c: c.search_blocks(id, verbose = verbose), verbose = verbose)
	
	# 103557.920 ms

	def _forAllChunks(self, function, range1 = range(REGION_SIZE_IN_CHUNKS), range2 = range(REGION_SIZE_IN_CHUNKS), verbose = 0):
		aChunk = None
		#time1 = time.time()
		for i in range1:
			for j in range2:
				if(self.inclusionCheck != None):
					if(not self.inclusionCheck(i * chunk.CHUNK_SIZE + self.x, j * chunk.CHUNK_SIZE + self.z)):
						continue
				try:
					aChunk = self.chunkByIndex(i, j)
				except (anvil.errors.ChunkNotFound, IndexError) as e:
					if(verbose >= constants.VERBOSE_ERRORS):
						print(e)
					continue
				try:
					for res in function(aChunk):
						yield res
				except Exception as e:
					if(verbose >= constants.VERBOSE_ERRORS):
						print(e)
					raise e
		#time2 = time.time()
		#print('{:s} function took {:.3f} ms'.format("_forAllChunks", (time2-time1)*1000.0))
		
	def _forAllChunksThreaded(self, function, verbose = 0):
		#time1 = time.time()
		threads = []
		functionDump = dill.dumps(function)
		kwargs = {"inclusionCheck": dill.dumps(self.inclusionCheck), "verbose": verbose}
		try:
			for i in range(1, REGION_SIZE_IN_CHUNKS):
				threads.append(_DEFAULT_PROCESS_POOL.schedule(_searchChunksTread, (self.path, i, functionDump), kwargs))
			#print("Threads Generated")
			yield from self._forAllChunks(function, range1 = range(0, 1), verbose = verbose)
			#print(f"Threads output")
			for thr in threads:
				try:
					chunkRes = thr.result()
					for res in chunkRes:
						yield res
				except (TypeError, pebble.common.ProcessExpired) as e:
					pass
		except KeyboardInterrupt as e: 
			i = 0
			for thr in threads:
				if(thr.cancel()):
					print(f"Canceled {i}")
				i += 1
			raise e
		except Exception as e:
			if(verbose >= constants.VERBOSE_ERRORS):
				print(e)
			raise e
		#print("Threads Done")
		#time2 = time.time()
		#print('{:s} function took {:.3f} ms'.format("_forAllChunksThreaded", (time2-time1)*1000.0))
	
	def _coordsToChunkIndex(self, x, z):
		cx = (x - self.x) // chunk.CHUNK_SIZE
		cz = (z - self.z) // chunk.CHUNK_SIZE
		if(cx < 0 or cx > REGION_SIZE_IN_CHUNKS or cz < 0 or cz > REGION_SIZE_IN_CHUNKS):
			raise errors.CoordsNotInArea((cx, cz), self)
		return (cx, cz)

	@staticmethod
	def _getCoordsFromPath(path):
		return list(map(int, os.path.basename(path).split(".")[1:3]))

	@staticmethod
	def _regionIndexToCoords(i, j):
		return (i * REGION_SIZE,j * REGION_SIZE)

	@staticmethod
	def _coordsToRegionIndex(x, z):
		return (x // REGION_SIZE, z // REGION_SIZE)

	@staticmethod
	def _regionIndexToFileName(i, j):
		return f"r.{i}.{j}.mca"
	
	@staticmethod
	def _coordsToFilename(x, z):
		return Region._regionIndexToFileName(*Region._coordsToRegionIndex(x, z))

	def __str__(self):
		return f"<{type(self).__name__} at ({self.x}, {self.z})>"
