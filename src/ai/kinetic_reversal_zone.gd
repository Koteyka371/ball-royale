extends "res://src/ai/game_modes.gd"



var zone_spawn_timer = 0.0
var zone_spawn_interval = 5.0

func _init():
    self.name = "Kinetic Reversal Zone"

func setup(world, balls):
    .setup(world, balls)

func tick(world, balls, delta):
    .tick(world, balls, delta)

    self.zone_spawn_timer -= delta
    if self.zone_spawn_timer <= 0:
        self.zone_spawn_timer = self.zone_spawn_interval

        var hz = {
            "id": world.next_id,
            "x": randf_range(100, 700),
            "y": randf_range(100, 500),
            "radius": 150.0,
            "kind": "kinetic_reversal_zone",
            "damage": 0.0,
            "active": true,
            "duration": 15.0
        }
        world.next_id += 1
        if not "hazards" in world.arena:
            world.arena.hazards = []
        world.arena.hazards.append(hz)
        if world.has_method("add_event"):
            world.add_event("kinetic_reversal_zone_spawned", {"x": hz.x, "y": hz.y, "radius": hz.radius})

    if "hazards" in world.arena:
        var i = world.arena.hazards.size() - 1
        while i >= 0:
            var h = world.arena.hazards[i]
            var h_kind = ""
            if "kind" in h: h_kind = h.kind
            elif typeof(h) == TYPE_DICTIONARY and h.has("kind"): h_kind = h["kind"]
            elif typeof(h) == TYPE_OBJECT and h.has_method("get_meta") and h.has_meta("kind"): h_kind = h.get_meta("kind")

            if h_kind == "kinetic_reversal_zone":
                var dur = 0.0
                if "duration" in h:
                    h.duration -= delta
                    dur = h.duration
                elif typeof(h) == TYPE_DICTIONARY and h.has("duration"):
                    h["duration"] -= delta
                    dur = h["duration"]

                if dur <= 0:
                    var h_x = 0
                    var h_y = 0
                    if "x" in h: h_x = h.x
                    elif typeof(h) == TYPE_DICTIONARY and h.has("x"): h_x = h["x"]
                    if "y" in h: h_y = h.y
                    elif typeof(h) == TYPE_DICTIONARY and h.has("y"): h_y = h["y"]

                    world.arena.hazards.remove(i)
                    if world.has_method("add_event"):
                        world.add_event("kinetic_reversal_zone_despawned", {"x": h_x, "y": h_y})
            i -= 1
