import argparse, os, glob

from . import world, nbt_util, errors, constants

def createSearchTags(tags):
	return list(map(nbt_util.TAG_Search.fromStr, tags))

def getNumberOfChunksWithInArea(x0, z0, x1, z1, stepSize = nbt_util.CHUNK_SIZE):
	return ((x1 - x0) * (z1 - z0)) / stepSize

def getNumberOfChunks(args):
	if(args.radius):
		return getNumberOfChunksWithInArea(-args.radius, -args.radius, args.radius, args.radius)
	elif(args.area):
		return getNumberOfChunksWithInArea(args.area[0], args.area[1], args.area[2], args.area[3])
	elif(args.chunk):
		return 1
	return 0

def getChunksWithInRadius(w, x, z, r, stepSize = nbt_util.CHUNK_SIZE, verbose = 0):
	yield from getChunksWithInArea(w, x - r, z - r, x + r, z + r, stepSize = stepSize, verbose = verbose)

def getChunksWithInArea(w, x0, z0, x1, z1, stepSize = nbt_util.CHUNK_SIZE, verbose = 0):
	for i in range(x0, x1, stepSize):
		for j in range(z0, z1, stepSize):
			try:
				coord, chunk = w.get_chunk_by_coords(x0 + i, z0 + j)
				if(chunk):
					yield chunk
			except KeyboardInterrupt as e:
				raise e
			except Exception as e:
				if(verbose >= constants.VERBOSE_ERRORS):
					print(e)

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
		if(verbose >= constants.VERBOSE_TAGS):
			print(f"{pos}\n {tile.pretty_tree()}\n")
		else:
			print(f"{pos}, {block.id}, {tile}")

def searchEntities(area, tags, verbose = 0):
	for pos, entity in area.search(keys = ["Entities"], tags = tags, verbose = verbose):
		if(verbose >= constants.VERBOSE_TAGS):
			print(f"{pos}\n {entity.pretty_tree()}\n")
		else:
			print(f"{pos}, {entity['id'].value}", end = "")
			if("CustomName" in entity):
				print(f", {entity['CustomName'].value}", end = "")
			print("")
	
def searchTiles(area, tags, verbose = 0):
	for pos, tile in area.search(keys = ["TileEntities"], tags = tags, verbose = verbose):
		if(verbose >= constants.VERBOSE_TAGS):
			print(f"{pos}\n {tile.pretty_tree()}\n")
		else:
			print(f"{pos}, {tile['id'].value}", end = "")
			if("SpawnData" in tile and "id" in tile['SpawnData']):
				print(f", {tile['SpawnData']['id'].value}", end = "")
			print("")

def searchStructures(area, tags, verbose = 0):
	for pos, structure in area.search(keys = [["Structures", "Starts"]], tags = tags, verbose = verbose):
		if(verbose >= constants.VERBOSE_TAGS):
			print(f"{pos}\n {structure.pretty_tree()}\n")
		else:
			print(f"{pos}, {structure['id'].value}")


def searchDragons(area, tags, verbose = 0):
	for pos, entity in area.search(keys = ["Entities"], tags = tags, verbose = verbose):
		if(verbose >= constants.VERBOSE_TAGS):
			print(f"{pos}\n {entity.pretty_tree()}\n")
		else:
			print(f"{pos}, {entity['id'].value}, Gender: {entity['Gender'].value}, Stage: {entity['AgeTicks'].value / 24000 / 25}, Sleeping: {entity['Sleeping']}", end = "")
			if("CustomName" in entity):
				print(f", {entity['CustomName'].value}", end = "")
			print("")

def searchNBT(area, tags, verbose = 0):
	for pos, tag in area.search(keys = [], tags = tags, verbose = verbose):
		if(verbose >= constants.VERBOSE_TAGS):
			print(f"{pos}\n {tag.pretty_tree()}\n")
		else:
			print(f"{pos}, {tag}")

def main():
	parser = argparse.ArgumentParser(description = "Script to search for things in a MineCraft world. Searches are limitied to full chunks.")
	parser.add_argument("-d", "--world_dir", metavar = "PATH", required = True, default = "", type = str, help = "the path to the MineCraft world dir")
	parser.add_argument("-v", "--verbose", metavar = "NUMBER", default = 2, type = int, help = "how much information to output. Can be {0:minimal, 1:low, 2:default, 3:more, 4:high, 5:tags, 6:errors}. (2)")
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

	tags = []

	if(args.command != "blocks"):
		if("id" in args and args.id != ""):
			tags.append(nbt_util.idToTAG_Search(args.id))
		
		if("name" in args and args.name != ""):
			tags.append(nbt_util.nameToTAG_Search(args.name))

		if("tags" in args and len(args.tags) > 0):
			tags.extend(createSearchTags(args.tags))
		
		if(args.verbose >= constants.VERBOSE_MEDIUM):
			print(f"Searching for {', '.join(map(str, tags))}")

	try:
		for w, name in getWorlds(args):
			if(args.verbose >= constants.VERBOSE_LOW):
				print(f"Searching {name}")
			for area in getAreas(w, args):
				if(area):
					if(((getNumberOfChunks(args) < 21 and args.verbose >= constants.VERBOSE_MORE) or args.verbose >= constants.VERBOSE_HIGH) and type(area) != world.World):
						print(f"Searching {area}")
					if(args.command == "blocks"):
						searchBlocks(area, args.id, verbose = args.verbose)
					elif(args.command == "entities"):
						searchEntities(area, tags, verbose = args.verbose)
					elif(args.command == "tiles"):
						searchTiles(area, tags, verbose = args.verbose)
					elif(args.command == "structures"):
						searchStructures(area, tags, verbose = args.verbose)
					elif(args.command == "nbt"):
						searchNBT(area, tags, verbose = args.verbose)
					elif(args.command == "dragons"):
						searchDragons(area, tags, verbose = args.verbose)
	except errors.TagsCategoryNotFoundInChunk as e:
		print(f"{e}")
		if(args.verbose < 5):
			print("\nTry running with verbose set to five (-v 5) to see what keys exists in '" + e.getLookupPath() + "'")

	except KeyboardInterrupt as e:
		pass

if(__name__ == "__main__"):
	main()

