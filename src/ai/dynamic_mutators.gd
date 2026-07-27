extends Node

var name: String = "Dynamic Weather Mutators"
var description: String = "Cycles through thunderstorm, blizzard, and sandstorm every 10 seconds."
var weather_timer: float = 10.0
var lightning_timer: float = 2.0
var current_weather: String = "blizzard"
var weathers: Array = ["thunderstorm", "blizzard", "sandstorm"]

func _init() -> void:
    pass

func setup(world, balls: Array) -> void:
    if world != null:
        if typeof(world) == TYPE_DICTIONARY:
            if not world.has("arena"):
                world["arena"] = {"hazards": []}
            elif typeof(world["arena"]) == TYPE_DICTIONARY and not world["arena"].has("hazards"):
                world["arena"]["hazards"] = []
        elif typeof(world) == TYPE_OBJECT:
            if not "arena" in world:
                pass
            elif world.arena != null:
                if not "hazards" in world.arena:
                    world.arena.hazards = []

    current_weather = weathers[randi() % weathers.size()]
    weather_timer = 10.0
    lightning_timer = 2.0

    for b in balls:
        var b_type = null
        if typeof(b) == TYPE_DICTIONARY:
            b_type = b.get("ball_type", null)
        elif typeof(b) == TYPE_OBJECT:
            b_type = b.get("ball_type")

        if b_type != "spectator":
            if typeof(b) == TYPE_DICTIONARY:
                if not b.has("base_speed"): b["base_speed"] = b.get("speed", 100.0)
                if not b.has("base_perception_radius"): b["base_perception_radius"] = b.get("perception_radius", 250.0)
            elif typeof(b) == TYPE_OBJECT:
                if b.get("base_speed") == null: b.set("base_speed", b.get("speed"))
                if b.get("base_perception_radius") == null: b.set("base_perception_radius", b.get("perception_radius"))

func tick(world, balls: Array, delta: float = 0.016) -> void:
    weather_timer -= delta
    if weather_timer <= 0.0:
        weather_timer = 10.0
        current_weather = weathers[randi() % weathers.size()]

    if current_weather == "thunderstorm":
        lightning_timer -= delta
        if lightning_timer <= 0.0:
            lightning_timer = 2.0

            var hazards = null
            if typeof(world) == TYPE_DICTIONARY and world.has("arena") and typeof(world["arena"]) == TYPE_DICTIONARY and world["arena"].has("hazards"):
                hazards = world["arena"]["hazards"]
            elif typeof(world) == TYPE_OBJECT and "arena" in world and world.arena != null and "hazards" in world.arena:
                hazards = world.arena.hazards

            if hazards != null:
                var strike = {
                    "kind": "lightning_strike",
                    "x": randf_range(100.0, 700.0),
                    "y": randf_range(100.0, 500.0),
                    "radius": 40.0,
                    "damage": 30.0,
                    "duration": 0.5
                }
                hazards.append(strike)

    for b in balls:
        var b_type = null
        if typeof(b) == TYPE_DICTIONARY: b_type = b.get("ball_type", null)
        elif typeof(b) == TYPE_OBJECT: b_type = b.get("ball_type")

        if b_type != "spectator":
            var base_speed = 100.0
            var base_perc = 250.0
            if typeof(b) == TYPE_DICTIONARY:
                base_speed = b.get("base_speed", 100.0)
                base_perc = b.get("base_perception_radius", 250.0)
            elif typeof(b) == TYPE_OBJECT:
                if b.get("base_speed") != null: base_speed = b.get("base_speed")
                if b.get("base_perception_radius") != null: base_perc = b.get("base_perception_radius")

            if current_weather == "blizzard":
                if typeof(b) == TYPE_DICTIONARY:
                    b["speed"] = base_speed * 0.5
                    b["perception_radius"] = base_perc
                elif typeof(b) == TYPE_OBJECT:
                    b.set("speed", base_speed * 0.5)
                    b.set("perception_radius", base_perc)
            elif current_weather == "sandstorm":
                if typeof(b) == TYPE_DICTIONARY:
                    b["speed"] = base_speed
                    b["perception_radius"] = base_perc * 0.3
                elif typeof(b) == TYPE_OBJECT:
                    b.set("speed", base_speed)
                    b.set("perception_radius", base_perc * 0.3)
            else:
                if typeof(b) == TYPE_DICTIONARY:
                    b["speed"] = base_speed
                    b["perception_radius"] = base_perc
                elif typeof(b) == TYPE_OBJECT:
                    b.set("speed", base_speed)
                    b.set("perception_radius", base_perc)

    var hazards = null
    if typeof(world) == TYPE_DICTIONARY and world.has("arena") and typeof(world["arena"]) == TYPE_DICTIONARY and world["arena"].has("hazards"):
        hazards = world["arena"]["hazards"]
    elif typeof(world) == TYPE_OBJECT and "arena" in world and world.arena != null and "hazards" in world.arena:
        hazards = world.arena.hazards

    if hazards != null:
        var to_remove = []
        for i in range(hazards.size()):
            var hazard = hazards[i]
            var h_kind = ""
            var h_dur = 0.0
            if typeof(hazard) == TYPE_DICTIONARY:
                h_kind = hazard.get("kind", "")
                h_dur = hazard.get("duration", 0.0)
            elif typeof(hazard) == TYPE_OBJECT:
                if hazard.get("kind") != null: h_kind = hazard.get("kind")
                if hazard.get("duration") != null: h_dur = hazard.get("duration")

            if h_kind == "lightning_strike":
                h_dur -= delta
                if typeof(hazard) == TYPE_DICTIONARY:
                    hazard["duration"] = h_dur
                elif typeof(hazard) == TYPE_OBJECT:
                    hazard.set("duration", h_dur)

                if h_dur <= 0.0:
                    to_remove.append(i)
                else:
                    var h_x = 0.0
                    var h_y = 0.0
                    var h_rad = 0.0
                    var h_dmg = 0.0
                    if typeof(hazard) == TYPE_DICTIONARY:
                        h_x = hazard.get("x", 0.0)
                        h_y = hazard.get("y", 0.0)
                        h_rad = hazard.get("radius", 0.0)
                        h_dmg = hazard.get("damage", 0.0)
                    elif typeof(hazard) == TYPE_OBJECT:
                        if hazard.get("x") != null: h_x = hazard.get("x")
                        if hazard.get("y") != null: h_y = hazard.get("y")
                        if hazard.get("radius") != null: h_rad = hazard.get("radius")
                        if hazard.get("damage") != null: h_dmg = hazard.get("damage")

                    for b in balls:
                        var alive = true
                        if typeof(b) == TYPE_DICTIONARY: alive = b.get("alive", true)
                        elif typeof(b) == TYPE_OBJECT:
                            if b.get("alive") != null: alive = b.get("alive")

                        if alive:
                            var b_x = 0.0
                            var b_y = 0.0
                            if typeof(b) == TYPE_DICTIONARY:
                                b_x = b.get("x", 0.0)
                                b_y = b.get("y", 0.0)
                            elif typeof(b) == TYPE_OBJECT:
                                if b.get("x") != null: b_x = b.get("x")
                                if b.get("y") != null: b_y = b.get("y")

                            var dx = b_x - h_x
                            var dy = b_y - h_y
                            if sqrt(dx*dx + dy*dy) < h_rad:
                                var dmg = h_dmg * delta
                                if typeof(b) == TYPE_DICTIONARY:
                                    if b.has("hp"):
                                        b["hp"] -= dmg
                                        if b["hp"] <= 0.0:
                                            b["alive"] = false
                                elif typeof(b) == TYPE_OBJECT:
                                    if b.has_method("take_damage"):
                                        b.take_damage(dmg)
                                    elif "hp" in b:
                                        b.set("hp", b.get("hp") - dmg)
                                        if b.get("hp") <= 0.0:
                                            b.set("alive", false)

        to_remove.reverse()
        for idx in to_remove:
            hazards.remove_at(idx)
