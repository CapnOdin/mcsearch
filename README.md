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
python -m mcsearch --dir <path-to-mc-world> -n tiles --tags id=CONTAINS(mob_spawner) id=CONTAINS(blaze)
```

Searching for all blaze spawners in the nether
```
python -m mcsearch --dir <path-to-mc-world> -n tiles --tags id=CONTAINS(mob_spawner) id=CONTAINS(blaze)
```