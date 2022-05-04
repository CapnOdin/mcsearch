from nbt import nbt

import re

ANY = None

CHUNK_SIZE = 16

class TAG_Search:
	def __init__(self, value = None, name = None, type = None):
		self.name = name
		self.value = value
		self.type = type

	def equals(self, other):
		return self.type == type(other) and self.equalsName(other) and self.equalsValue(other)
	
	def equalsName(self, other):
		return self.name == ANY or self.name == other.name

	def equalsValue(self, other):
		return self.value == ANY or self.value == other.value
	
	def __str__(self):
		return f"<{type(self).__name__} {self.name if self.name != ANY else 'ANY'} = {self.value if self.value != ANY else 'ANY'}>"
	
	def __repr__(self):
		return str(self)

class TAG_Any(TAG_Search):
	def equals(self, other):
		return self.equalsName(other) and self.equalsValue(other)

class TAG_StrMatch(TAG_Any):
	def equalsValue(self, other):
		return self.value == ANY or str(self.value) == str(other.value)

class TAG_StrPartialMatch(TAG_Any):
	def equalsValue(self, other):
		return self.value == ANY or str(self.value) in str(other.value)

class TAG_Regex(TAG_Any):
	def __init__(self, value = None, name = None, type = None):
		super().__init__(value = value, name = name, type = type)
		self.rxName = re.compile(self.name) if name != ANY else None
		self.rxValue = re.compile(self.value) if value != ANY else None

	def equalsName(self, other):
		return self.name == ANY or self.rxName.search(str(other.name))

	def equalsValue(self, other):
		return self.value == ANY or self.rxValue.search(str(other.value))

def print_chunk_tiles(chunk):
	for ttag in chunk.tile_entities:
		print(ttag.pretty_tree())
		print("")

def nbt_tag_contains_tags(nbt_tag, tags):
	found = nbt_tag_number_of_contained_tags(nbt_tag, tags)
	return sum(found) == len(tags)

def nbt_tag_number_of_contained_tags(nbt_tag, tags, found = None):
	if(found == None):
		found = [0] * len(tags)
	
	if(type(nbt_tag) == nbt.TAG_Compound or type(nbt_tag) == nbt.TAG_List):
		for tag in nbt_tag.tags:
			if(type(tag) == nbt.TAG_Compound or type(tag) == nbt.TAG_List):
				nbt_tag_number_of_contained_tags(tag, tags, found = found)
			else:
				for index, test_tag in enumerate(tags):
					if(test_tag.equals(tag)):
						found[index] = 1
	return found

def nbt_tag_get_pos(nbt_tag):
	if("x" in nbt_tag and "y" in nbt_tag and "z" in nbt_tag):
		return (nbt_tag["x"].value, nbt_tag["y"].value, nbt_tag["z"].value)
	if("Pos" in nbt_tag):
		pos = nbt_tag["Pos"]
		return (pos[0].value, pos[1].value, pos[2].value)
	if("ChunkX" in nbt_tag and "ChunkZ" in nbt_tag):
		return (nbt_tag["ChunkX"].value * CHUNK_SIZE, 0, nbt_tag["ChunkZ"].value * CHUNK_SIZE)
	return None

