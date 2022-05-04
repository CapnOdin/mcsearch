import argparse, re, os, glob

from . import world, nbt_util

def convertAnyToNone(string):
	return string if string != "ANY" else nbt_util.ANY

def parseSearchTagKeywords(tagStr):
	key, val = tagStr.split("=", maxsplit = 1)
	match = re.search("^(\w+)\((.+)\)", val)
	if(match):
		if(match.group(1) == "C" or match.group(1) == "CONTAINS"):
			return nbt_util.TAG_StrPartialMatch(value = convertAnyToNone(match.group(2)), name = convertAnyToNone(key))
		elif(match.group(1) == "R" or match.group(1) == "REGEX"):
			return nbt_util.TAG_Regex(value = convertAnyToNone(match.group(2)), name = convertAnyToNone(key))
	return nbt_util.TAG_StrMatch(value = convertAnyToNone(val), name = convertAnyToNone(key))

def createSearchTags(tags):
	return list(map(parseSearchTagKeywords, tags))

def getChunksWithInRadius(w, x, z, r, stepSize = nbt_util.CHUNK_SIZE):
	yield from getChunksWithInArea(w, x - r, z - r, x + r, z + r, stepSize = stepSize)

def getChunksWithInArea(w, x0, z0, x1, z1, stepSize = nbt_util.CHUNK_SIZE):
	for i in range(x0, x1, stepSize):

		for j in range(z0, z1, stepSize):
			try:
				coord, chunk = w.get_chunk_by_coords(x0 + i, z0 + j)
				if(chunk):
					yield chunk
			except:
				pass

def getAreas(w, args):
	if(args.radius):
		if(args.chunk):
			yield from getChunksWithInRadius(w, args.chunk[0], args.chunk[1], args.radius)
		else:
			yield from getChunksWithInRadius(w, 0, 0, args.radius)
	elif(args.area):
		yield from getChunksWithInArea(w, args.area[0], args.area[1], args.area[2], args.area[3])
	elif(args.chunk):
		yield w.get_chunk_by_coords(*args.chunk)[1]
	else:
		yield w

def getWorlds(args):
	if(args.overworld or (not args.nether and not args.end and not len(args.dim))):
		yield (world.World(os.path.join(args.world_dir, "region")), "OverWorld")
	if(args.nether):
		yield (world.World(os.path.join(args.world_dir, "DIM-1", "region")), "Nether")
	if(args.end):
		yield (world.World(os.path.join(args.world_dir, "DIM1", "region")), "End")

	for dimName in args.dim:
		for path in glob.iglob(os.path.join(args.world_dir, "dimensions", dimName, "**", "region"), recursive = True):
			yield (world.World(path), dimName.capitalize())

def searchBlocks(area, id, verbose = 0):
	for pos, block, tile in area.search(id = id, searchBlocks = True, verbose = verbose):
		if(verbose > 4):
			print(f"{pos}\n {tile.pretty_tree()}\n")
		else:
			print(f"{pos}, {block.id}, {tile}")

def searchEntities(area, id, name, tags, verbose = 0):
	id = id if len(id) else None
	name = nbt_util.ANY if name == "ANY" else (name if len(name) > 0 else "")
	for pos, entity in area.search(id = id, name = name, keys = ["Entities"], tags = tags, verbose = verbose):
		if(verbose > 4):
			print(f"{pos}\n {entity.pretty_tree()}\n")
		else:
			print(f"{pos}, {entity['id'].value}", end = "")
			if("CustomName" in entity):
				print(f", {entity['CustomName'].value}", end = "")
			print("")
	
def searchTiles(area, id, tags, verbose = 0):
	id = id if len(id) else None
	for pos, tile in area.search(id = id, keys = ["TileEntities"], tags = tags, verbose = verbose):
		if(verbose > 4):
			print(f"{pos}\n {tile.pretty_tree()}\n")
		else:
			print(f"{pos}, {tile['id'].value}", end = "")
			if("SpawnData" in tile and "id" in tile['SpawnData']):
				print(f", {tile['SpawnData']['id'].value}", end = "")
			print("")

def searchStructures(area, id, tags, verbose = 0):
	id = id if len(id) else None
	for pos, structure in area.search(id = id, keys = [["Structures", "Starts"]], tags = tags, verbose = verbose):
		if(verbose > 4):
			print(f"{pos}\n {structure.pretty_tree()}\n")
		else:
			print(f"{pos}, {structure['id'].value}")


def searchDragons(area, id, name, tags, verbose = 0):
	id = id if len(id) else None
	name = nbt_util.ANY if name == "ANY" else (name if len(name) > 0 else "")
	for pos, entity in area.search(id = id, name = name, keys = ["Entities"], tags = tags, verbose = verbose):
		if(verbose > 4):
			print(f"{pos}\n {entity.pretty_tree()}\n")
		else:
			print(f"{pos}, {entity['id'].value}, Gender: {entity['Gender'].value}, Stage: {entity['AgeTicks'].value / 24000 / 25}, Sleeping: {entity['Sleeping']}", end = "")
			if("CustomName" in entity):
				print(f", {entity['CustomName'].value}", end = "")
			print("")

def searchNBT(area, tags, verbose = 0):
	for pos, tag in area.search(id = id, keys = [], tags = tags, verbose = verbose):
		if(verbose > 4):
			print(f"{pos}\n {tag.pretty_tree()}\n")
		else:
			print(f"{pos}, {tag}")

def main():
	parser = argparse.ArgumentParser(description = "Script to search for things in a MineCraft world. Searches are limitied to full chunks.")
	parser.add_argument("-d", "--world_dir", metavar = "PATH", required = True, default = "", type = str, help = "the path to the MineCraft world dir")
	parser.add_argument("-v", "--verbose", metavar = "NUMBER", default = 0, type = int, help = "how much information to output. Goes from 0 to 5. (0)")
	parser.add_argument("-c", "--chunk", metavar = ("X", "Z"), nargs = 2, default = None, type = int, help = "the cordinates in a specific chunk to search")
	parser.add_argument("-r", "--radius", metavar = "DISTANCE", default = 0, type = int, help = "the number of blocks out from the specidied chunk to search")
	parser.add_argument("-a", "--area", metavar = ("X0", "Z0", "X1", "Z1"), nargs = 4, default = None, type = int, help = "the area in block coordinates to search")

	parser.add_argument("-n", "--nether", action = "store_true", help = "search in the nether")
	parser.add_argument("-e", "--end", action = "store_true", help = "search in the end")
	parser.add_argument("-o", "--overworld", action = "store_true", help = "search in the overworld")

	parser.add_argument("-m", "--dim", metavar = "NAME", action = "append", default = list(), help = "name of additional dimentions to search (works with dimentions in the dimention directory)")

	subparsers = parser.add_subparsers(title = "subcommands", dest = "command", description = "valid subcommands", help = "COMMAND -h for additional help.")

	blocks = subparsers.add_parser("blocks", description = "Search the world for blocks with an ID.")
	blocks.add_argument("id", metavar = "ID", type = str, help = 'the block id of the block to find e.g. "minecraft:diamont_ore"')

	entities = subparsers.add_parser("entities", description = "Search the nbt data for entities.")
	entities.add_argument("-i", "--id", metavar = "ID", default = "", type = str, help = 'the id of the entities to find e.g. "minecraft:wolf"')
	entities.add_argument("-n", "--name", metavar = "NAME", default = "", type = str, help = 'the name of a named entity. Use "ANY" for any named entity')
	entities.add_argument("-t", "--tags", metavar = "KEY=VALUE", nargs = "*", default = list(), help = 'a list of aditional nbt search terms that must all be found e.g. "age=1"')

	tiles = subparsers.add_parser("tiles", description = "Search the nbt data for tile entities.")
	tiles.add_argument("-i", "--id", metavar = "ID", default = "", type = str, help = 'the block id of the tile entities to find e.g. "minecraft:spawner"')
	tiles.add_argument("-t", "--tags", metavar = "KEY=VALUE", nargs = "*", default = list(), help = 'a list of aditional nbt search terms that must all be found e.g. "id=minecraft:zombie"')

	structures = subparsers.add_parser("structures", description = "Search the nbt data for structures.")
	structures.add_argument("-i", "--id", metavar = "ID", default = "", type = str, help = 'the id of the structures to find e.g. "minecraft:fortress"')

	nbt = subparsers.add_parser("nbt", description = "Search the nbt data for tags.")
	nbt.add_argument("tags", metavar = "KEY=VALUE", nargs = "*", default = list(), help = 'a list of nbt search terms that must all be found e.g. "id=minecraft:zombie"')

	dragons = subparsers.add_parser("dragons", description = "Search the nbt data for entities.")
	dragons.add_argument("-i", "--id", metavar = "ID", default = "", type = str, help = 'the id of the entities to find e.g. "minecraft:wolf"')
	dragons.add_argument("-n", "--name", metavar = "NAME", default = "", type = str, help = 'the name of a named entity. Use "ANY" for any named entity')
	dragons.add_argument("-t", "--tags", metavar = "KEY=VALUE", nargs = "*", default = list(), help = 'a list of aditional nbt search terms that must all be found e.g. "Gender=1"')

	args = parser.parse_args()

	tags = None

	if("tags" in args and len(args.tags) > 0):
		tags = createSearchTags(args.tags)
		print(tags)

	try:
		for w, name in getWorlds(args):
			if(args.verbose > 0):
				print(f"Searching {name}")
			for area in getAreas(w, args):
				if(area):
					if(args.verbose > 1):
						print(f"Searching {area}")
					if(args.command == "blocks"):
						searchBlocks(area, args.id, verbose = args.verbose)
					elif(args.command == "entities"):
						searchEntities(area, args.id, args.name, tags, verbose = args.verbose)
					elif(args.command == "tiles"):
						searchTiles(area, args.id, tags, verbose = args.verbose)
					elif(args.command == "structures"):
						searchStructures(area, args.id, tags, verbose = args.verbose)
					elif(args.command == "nbt"):
						searchNBT(area, tags, verbose = args.verbose)
					elif(args.command == "dragons"):
						searchDragons(area, args.id, args.name, tags, verbose = args.verbose)
	except KeyboardInterrupt as e:
		pass

if(__name__ == "__main__"):
	main()

