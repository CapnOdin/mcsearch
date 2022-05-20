import anvil

import re

from nbt import nbt

from . import searchable, nbt_util, errors

CHUNK_SIZE = nbt_util.CHUNK_SIZE

class StringMatch:
	def __init__(self, value):
		self.value = value

	def equals(self, string):
		return self.value == nbt_util.ANY or self.value == string
	
	def fromStr(string):
		match = re.search("^(\w+)\((.+)\)", string)
		if(match):
			if(match.group(1) == "C" or match.group(1) == "CONTAINS"):
				return PartialMatch(nbt_util.convertAnyToNone(match.group(2)))
			elif(match.group(1) == "R" or match.group(1) == "REGEX"):
				return RegexMatch(nbt_util.convertAnyToNone(match.group(2)))
		return StringMatch(nbt_util.convertAnyToNone(string))

class PartialMatch(StringMatch):
	def equals(self, string):
		return self.value == nbt_util.ANY or self.value in string

class RegexMatch(StringMatch):
	def __init__(self, value):
		super().__init__(value)
		self.value = re.compile(value)

	def equals(self, string):
		return self.value == nbt_util.ANY or self.value.search(string)

class Chunk(searchable.Searchable, anvil.Chunk):
	def search_nbt(self, tags, keys = None, verbose = 0):
		if(keys):
			yield from self.__check_tags(tags, keys, verbose = verbose)
		else:
			yield from self.__check_tags(tags, self.data, verbose = verbose)
	
	def search_blocks(self, id, verbose = 0):
		offx = self.data["xPos"].value * CHUNK_SIZE
		offz = self.data["zPos"].value * CHUNK_SIZE

		isOld = type(self.get_block(0, 255, 0)) is anvil.OldBlock
		matchID = StringMatch.fromStr(id)

		for index, block in enumerate(self.stream_chunk(index = 0, section = None)):
			if(isOld):
				block = anvil.Block.from_numeric_id(block_id = block.id, data = block.data)
			if(matchID.equals(block.name())):
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


