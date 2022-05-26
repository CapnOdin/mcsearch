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

def searchChunks20XX1(path, i, function, verbose = 0):
	r = Region.from_file(path)
	function = dill.loads(function)
	aChunk = None
	for j in range(REGION_SIZE_IN_CHUNKS):
		try:
			aChunk = r.chunkByIndex(i, j)
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

def searchChunks20XX2(path, i, function, verbose = 0):
	lst = []
	try:
		#print(f"Thread {i} start")
		r = Region.from_file(path)
		function = dill.loads(function)
		aChunk = None
		for j in range(REGION_SIZE_IN_CHUNKS):
			try:
				aChunk = r.chunkByIndex(i, j)
			except (anvil.errors.ChunkNotFound, IndexError) as e:
				if(verbose >= constants.VERBOSE_ERRORS):
					print(e)
				continue
			lst.append([])
			try:
				for res in function(aChunk):
					lst[-1].append(res)
			except Exception as e:
				if(verbose >= constants.VERBOSE_ERRORS):
					print(e)
				raise e
		#print(f"Thread {i} done")
	except Exception as e:
		pass
	return lst

def forAllChunksThreaded20XX(path, function, verbose = 0):
	#time1 = time.time()
	function = dill.dumps(function)
	threads = []
	try:
		for i in range(1, REGION_SIZE_IN_CHUNKS):
			threads.append(_DEFAULT_PROCESS_POOL.schedule(searchChunks20XX2, (path, i, function), {"verbose": verbose}))
		#print("Threads Generated")
		yield from searchChunks20XX1(path, 0, function, verbose = verbose)
		#print(f"Threads output")
		for thr in threads:
			try:
				chunkRes = thr.result()
				for res in chunkRes:
					for res2 in res:
						yield res2
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
	#print('{:s} function took {:.3f} ms'.format("__forAllChunksThreaded20XX", (time2-time1)*1000.0))


class Region(searchable.Searchable, anvil.Region, area.Area):
	def __init__(self, data: bytes, path = "", x = None, z = None):
		super().__init__(data)
		if((x == None or z == None) and path):
			x, z = self.__getCoordsFromPath(path)
		if(x != None and z != None):
			area.Area.__init__(self, x, z, REGION_SIZE, REGION_SIZE)
		self.path = path

	@classmethod
	def from_file(cls, path, x = None, z = None):
		r = super(Region, cls).from_file(path)
		r.path = path
		if(x == None or z == None):
			x, z = r.__getCoordsFromPath(path)
		if(x != None and z != None):
			area.Area.__init__(r, x, z, REGION_SIZE, REGION_SIZE)
		return r
	
	def __getCoordsFromPath(self, path):
		return list(map(int, os.path.basename(path).split(".")[1:3]))

	def chunkByIndex(self, i, j):
		return chunk.Chunk.from_region(self, i, j)

	def chunkByCoords(self, x, z):
		return self.chunkByIndex(*self.__coordsToChunkIndex(x, z))

	def search_nbt(self, tags, keys = None, verbose = 0):
		if(platform.python_implementation() == "PyPy"):
			yield from self.__forAllChunks(lambda c: c.search_nbt(tags, keys = keys, verbose = verbose), verbose = verbose)
		else:
			yield from forAllChunksThreaded20XX(self.path, lambda c: c.search_nbt(tags, keys = keys, verbose = verbose), verbose = verbose)

	def search_blocks(self, id, verbose = 0):
		#yield from self.__forAllChunks(lambda c: c.search_blocks(id, verbose = verbose), verbose = verbose)
		#yield from self.__forAllChunksThreaded100(lambda c: c.search_blocks(id, verbose = verbose), verbose = verbose)
		yield from forAllChunksThreaded20XX(self.path, lambda c: c.search_blocks(id, verbose = verbose), verbose = verbose)
		#yield from self.__forAllChunksThreaded4(id, lambda c: c.search_blocks(id, verbose = verbose), verbose = verbose)
	
	# 103557.920 ms

	def __forAllChunks(self, funtion, verbose = 0):
		aChunk = None
		#time1 = time.time()
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
		#time2 = time.time()
		#print('{:s} function took {:.3f} ms'.format("__forAllChunks", (time2-time1)*1000.0))
	
	def __coordsToChunkIndex(self, x, z):
		cx = (x - self.x) // chunk.CHUNK_SIZE
		cz = (z - self.z) // chunk.CHUNK_SIZE
		if(cx < 0 or cx > REGION_SIZE_IN_CHUNKS or cz < 0 or cz > REGION_SIZE_IN_CHUNKS):
			raise errors.CoordsNotInArea((cx, cz), self)
		return (cx, cz)

	def __str__(self):
		return f"<{type(self).__name__} at ({self.x}, {self.z})>"
