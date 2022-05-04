# McSearch

## Examples
Searching for all spawners in a 500 block radius around (0, 0)
```
python -m mcsearch --dir <path-to-mc-world> --chunk 0 0 -r 500 tiles --id minecraft:mob_spawner
```

Searching for all named wolfs
```
python -m mcsearch --dir <path-to-mc-world> entities --id minecraft:wolf --name ANY
```

Searching for all blaze spawners in the nether
```
python -m mcsearch --dir <path-to-mc-world> --nether tiles --tags id=CONTAINS(mob_spawner) id=CONTAINS(blaze)
```

Searching for all end cities in the end
```
python -m mcsearch --dir <path-to-mc-world> --end structures --tags id=CONTAINS(city)
```

Searching for all zombie and skeleton spawners
```
python -m mcsearch --dir <path-to-mc-world> tiles --tags id=CONTAINS(mob_spawner) id=REGEX(zombie|skeleton)
```

Searching for all twilightforest entities in the twilightforest dimention
```
python -m mcsearch --dir <path-to-mc-world> --dim twilightforest/twilightforest entities --tags id=C(twilightforest)
```