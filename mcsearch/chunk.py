import anvil

from nbt import nbt

from . import searchable, nbt_util, errors

CHUNK_SIZE = nbt_util.CHUNK_SIZE

class Chunk(searchable.Searchable, anvil.Chunk):
	def search_nbt(self, tags, keys = None, verbose = 0):
		#print(self.data["Structures"].pretty_tree())
		#print(self.data.pretty_tree())

		if(keys):
			yield from self.__check_tags(tags, keys, verbose = verbose)
		else:
			yield from self.__check_tags(tags, self.data, verbose = verbose)
	
	def search_blocks(self, id, verbose = 0):
		offx = self.data["xPos"].value * CHUNK_SIZE
		offz = self.data["zPos"].value * CHUNK_SIZE
		for index, block in enumerate(self.stream_chunk(index = 0, section = None)):
			if(block.name() == id):
				pos = self.__index_to_pos(index)
				yield ((pos[0] + offx, pos[1], pos[2] + offz), block, self.get_tile_entity(pos[0] + offx, pos[1], pos[2] + offz))

	def __index_to_pos(self, index, offx = 0, offy = 0, offz = 0):
		# y * 256 + z * 16 + x
		return ((index % 16) + offx, index // 256 + offy, (index % 256) // 16 + offz)
	
	def __check_tags(self, tags, keys, verbose = 0):
		for key in keys:
			data = self.__lookup_names_in_tag(key if type(key) is list else [key], self.data, verbose = verbose)
			if(issubclass(data.__class__, nbt.TAG)):
				yield from self.__check_tag(data.tags, tags, verbose = verbose)
			else:
				yield from self.__check_tag(data, tags, verbose = verbose)

	def __check_tag(self, nbt_tags, tags, verbose = 0):
		for tag in nbt_tags:
			if(nbt_util.nbt_tag_contains_tags(tag, tags)):
				pos = nbt_util.nbt_tag_get_pos(tag)
				if(pos):
					pos = tuple(map(round, pos))
				yield (pos, tag)
	
	def __lookup_names_in_tag(self, names, tag, verbose = 0):
		res_tag = tag
		name = ""
		try:
			for i, name in enumerate(names):
				res_tag = res_tag[name]
		except KeyError as e:
			raise errors.TagsCategoryNotFoundInChunk(names[0:i] if i > 0 else [], self, name, verbose = verbose) from None
		return res_tag

	def __str__(self):
		offx = self.data["xPos"].value * CHUNK_SIZE
		offz = self.data["zPos"].value * CHUNK_SIZE
		return f"<{type(self).__name__} at ({offx}, {offz})>"


