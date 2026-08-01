extends "res://src/ai/game_modes.gd"

class SignalScramblerMode extends GameMode:
    var jammer_x = 0.0
    var jammer_y = 0.0
    var jammer_radius = 400.0
    var setup_done = false

    func _init():
        name = "Signal Scrambler Gadget"
        description = "A massive gadget at the center of the arena permanently scrambles homing missiles and drastically reduces AI perception in a large area."

    func setup(world, balls):
        setup_done = false

    func tick(world, balls, delta=0.016):
        super.tick(world, balls, delta)

        if not "arena" in world or typeof(world.arena) == TYPE_NIL:
            return

        var arena_width = 1000.0
        if "width" in world.arena:
            arena_width = float(world.arena.width)
        var arena_height = 1000.0
        if "height" in world.arena:
            arena_height = float(world.arena.height)

        if not setup_done:
            jammer_x = arena_width / 2.0
            jammer_y = arena_height / 2.0
            setup_done = true

            if not "hazards" in world.arena:
                world.arena.hazards = []

            var h = {}
            if typeof(world.arena.hazards) == TYPE_ARRAY and world.arena.hazards.size() > 0 and typeof(world.arena.hazards[0]) == TYPE_OBJECT:
                var HazardType = load("res://src/arena/hazard.gd")
                if HazardType != null:
                    h = HazardType.new(world.arena.hazards.size() + 12000, jammer_x, jammer_y, "signal_scrambler", 400.0)
                    h.damage = 0.0
            else:
                h = {
                    "id": world.arena.hazards.size() + 12000,
                    "x": jammer_x,
                    "y": jammer_y,
                    "radius": jammer_radius,
                    "kind": "signal_scrambler",
                    "damage": 0.0,
                    "active": true
                }

            world.arena.hazards.append(h)
