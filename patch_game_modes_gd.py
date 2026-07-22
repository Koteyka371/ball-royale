with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

new_class = """
class FallingTilesRoyaleMode extends GameMode:
\tvar grid_size = 50.0
\tvar tiles = {}
\tvar timer = 0.0
\tvar phase = "wait"
\tvar warning_duration = 2.0
\tvar fall_duration = 3.0
\tvar active_tiles = []
\tvar falling_tiles = []
\tvar is_falling_tiles_royale = true
\tvar cols = 0
\tvar rows = 0
\t
\tfunc _init():
\t\tname = "Falling Tiles Royale"
\t\tdescription = "A battle royale variant where the arena is made up of a grid of tiles. Every few seconds, some tiles light up and then fall away, turning into bottomless pits."

\tfunc setup(world, balls):
\t\tsuper.setup(world, balls)
\t\ttiles = {}
\t\tvar arena_width = 1000.0
\t\tvar arena_height = 1000.0
\t\tif "arena" in world and world.arena != null:
\t\t\tarena_width = world.arena.get("width") if typeof(world.arena) == TYPE_DICTIONARY else world.arena.width
\t\t\tarena_height = world.arena.get("height") if typeof(world.arena) == TYPE_DICTIONARY else world.arena.height
\t\t
\t\tcols = int(arena_width / grid_size)
\t\trows = int(arena_height / grid_size)
\t\t
\t\tfor c in range(cols):
\t\t\tfor r in range(rows):
\t\t\t\ttiles[str(c) + "," + str(r)] = {"state": "normal"}
\t\t
\t\ttimer = 5.0
\t\tphase = "wait"

\tfunc tick(world, balls, delta=0.016):
\t\tsuper.tick(world, balls, delta)
\t\ttimer -= delta
\t\t
\t\tif phase == "wait":
\t\t\tif timer <= 0:
\t\t\t\tphase = "warning"
\t\t\t\ttimer = warning_duration
\t\t\t\tvar normal_tiles = []
\t\t\t\tfor k in tiles.keys():
\t\t\t\t\tif tiles[k]["state"] == "normal":
\t\t\t\t\t\tnormal_tiles.append(k)
\t\t\t\t
\t\t\t\tvar num_to_fall = int(max(1, int(normal_tiles.size() * 0.1)))
\t\t\t\tif num_to_fall > normal_tiles.size() - 4:
\t\t\t\t\tnum_to_fall = max(1, normal_tiles.size() - 4)
\t\t\t\t
\t\t\t\tfalling_tiles = []
\t\t\t\tnormal_tiles.shuffle()
\t\t\t\tfor i in range(min(num_to_fall, normal_tiles.size())):
\t\t\t\t\tfalling_tiles.append(normal_tiles[i])
\t\t\t\t\ttiles[normal_tiles[i]]["state"] = "warning"
\t\t\t\t
\t\t\t\tif typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
\t\t\t\t\tworld.add_event("tiles_warning", {"message": "Some tiles are lighting up!"})
\t\t\t\t\telif typeof(world) == TYPE_DICTIONARY and world.has("add_event"):
\t\t\t\t\t\tworld.add_event.call("tiles_warning", {"message": "Some tiles are lighting up!"})
\t\t\t\t\t
\t\telif phase == "warning":
\t\t\tif timer <= 0:
\t\t\t\tphase = "falling"
\t\t\t\ttimer = fall_duration
\t\t\t\tfor k in falling_tiles:
\t\t\t\t\ttiles[k]["state"] = "falling"
\t\t\t\tif typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
\t\t\t\t\tworld.add_event("tiles_falling", {"message": "Tiles are falling!"})
\t\t\t\t\telif typeof(world) == TYPE_DICTIONARY and world.has("add_event"):
\t\t\t\t\t\tworld.add_event.call("tiles_falling", {"message": "Tiles are falling!"})
\t\t\t\t\t
\t\telif phase == "falling":
\t\t\tif timer <= 0:
\t\t\t\tphase = "wait"
\t\t\t\ttimer = randf_range(4.0, 8.0)
\t\t\t\tfor k in falling_tiles:
\t\t\t\t\ttiles[k]["state"] = "pit"
\t\t\t\tfalling_tiles.clear()
\t\t\t\t
\t\tfor b in balls:
\t\t\tvar is_alive = false
\t\t\tvar b_type = null
\t\t\tif typeof(b) == TYPE_DICTIONARY:
\t\t\t\tis_alive = b.get("alive", false)
\t\t\t\tb_type = b.get("ball_type", null)
\t\t\telse:
\t\t\t\tis_alive = b.alive if "alive" in b else false
\t\t\t\tb_type = b.ball_type if "ball_type" in b else null
\t\t\t\t
\t\t\tif not is_alive or b_type == "spectator":
\t\t\t\tcontinue
\t\t\t\t
\t\t\tvar bx = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else b.x
\t\t\tvar by = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else b.y
\t\t\tvar c = int(bx / grid_size)
\t\t\tvar r = int(by / grid_size)
\t\t\tvar k = str(c) + "," + str(r)
\t\t\t
\t\t\tif tiles.has(k):
\t\t\t\tvar state = tiles[k]["state"]
\t\t\t\tif state == "pit":
\t\t\t\t\tif typeof(b) == TYPE_OBJECT and b.has_method("take_damage"):
\t\t\t\t\t\tb.take_damage(9999.0)
\t\t\t\t\telse:
\t\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:
\t\t\t\t\t\t\tb["hp"] = 0.0
\t\t\t\t\t\t\tb["alive"] = false
\t\t\t\t\t\telse:
\t\t\t\t\t\t\tb.hp = 0.0
\t\t\t\t\t\t\tb.alive = false
\t\t\t\t\t
\t\t\t\t\tvar final_alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else b.alive
\t\t\t\t\tif not final_alive:
\t\t\t\t\t\tvar bid = b.get("id", null) if typeof(b) == TYPE_DICTIONARY else b.id
\t\t\t\t\t\tif typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
\t\t\t\t\t\t\tworld.add_event("ball_fell", {"id": bid})
\t\t\t\t\t\telif typeof(world) == TYPE_DICTIONARY and world.has("add_event"):
\t\t\t\t\t\t\tworld.add_event.call("ball_fell", {"id": bid})
"""

if "FallingTilesRoyaleMode extends GameMode" not in content:
    idx = content.rfind("GAME_MODES = {")
    if idx != -1:
        content = content[:idx] + new_class + "\n" + content[idx:]
        content = content.replace("GAME_MODES = {", "GAME_MODES = {\n\t\"falling_tiles_royale\": FallingTilesRoyaleMode.new(),")
        with open("src/ai/game_modes.gd", "w") as f:
            f.write(content)
        print("Added FallingTilesRoyaleMode to src/ai/game_modes.gd")
