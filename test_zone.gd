extends SceneTree
func _init():
    var arena = load("res://src/arena/procedural_arena.gd").new()
    arena.num_rooms = 100
    arena.generate()
    var count = 0
    for h in arena.hazards:
        if h.kind == "shrinking_zone":
            count += 1
    print("Found ", count, " shrinking zones in GDScript")
    quit()
