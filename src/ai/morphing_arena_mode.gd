extends GameMode

func _init() -> void:
    super._init()
    name = "Morphing Arena"
    description = "The arena smoothly morphs between different shapes every 60 seconds."

func setup(world, balls: Array) -> void:
    super.setup(world, balls)

    var MorphingArenaScript = load("res://src/arena/morphing_arena.gd")
    if MorphingArenaScript:
        var old_width = 2000.0
        if world.arena and "width" in world.arena:
            old_width = world.arena.width
        world.arena = MorphingArenaScript.new(old_width)
