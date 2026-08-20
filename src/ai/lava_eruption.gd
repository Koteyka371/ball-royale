extends "res://src/ai/game_modes.gd".GameMode

var eruption_timer = 0.0
var eruption_interval = 8.0
var eruptions = []
var puddles = []

func _init():
    super._init()
    name = "Lava Eruption Event"
    description = "A random event that periodically erupts lava fountains from the ground, leaving damaging puddles that players must navigate around during combat."
    eruption_timer = 0.0
    eruption_interval = 8.0
    eruptions = []
    puddles = []

func apply_dynamic_traits(world, balls, delta):
    super.apply_dynamic_traits(world, balls, delta)

    eruption_timer += delta

    if eruption_timer >= eruption_interval:
        eruption_timer = 0.0
        var num_eruptions = (randi() % 3) + 3 # Random integer between 3 and 5
        for _i in range(num_eruptions):
            var ex = randf_range(200.0, 800.0)
            var ey = randf_range(200.0, 800.0)
            eruptions.append({
                "x": ex,
                "y": ey,
                "timer": 0.0,
                "warning_duration": 2.0,
                "radius": 50.0
            })

    var new_eruptions = []
    for e in eruptions:
        e["timer"] += delta
        if e["timer"] >= e["warning_duration"]:
            if world.has_method("add_event"):
                world.add_event("lava_eruption", {"x": e["x"], "y": e["y"], "radius": e["radius"]})

            var puddle_radius = e["radius"] * 1.5
            puddles.append({
                "x": e["x"],
                "y": e["y"],
                "radius": puddle_radius,
                "duration": 10.0,
                "timer": 0.0
            })

            for b in balls:
                var is_alive = b.get("alive") if typeof(b) == TYPE_DICTIONARY else (b.alive if "alive" in b else true)
                if is_alive:
                    var bx = b.get("x") if typeof(b) == TYPE_DICTIONARY else b.x
                    var by = b.get("y") if typeof(b) == TYPE_DICTIONARY else b.y

                    var dx = bx - e["x"]
                    var dy = by - e["y"]
                    var dist = sqrt(dx*dx + dy*dy)

                    if dist <= puddle_radius:
                        if typeof(b) == TYPE_DICTIONARY:
                            b["z_velocity"] = b.get("z_velocity", 0.0) + 800.0
                            if b.get("weather_immunity_timer", 0.0) <= 0.0:
                                b["burn_timer"] = b.get("burn_timer", 0.0) + 5.0
                        else:
                            var zv = b.get_meta("z_velocity") if (b.has_method("has_meta") and b.has_meta("z_velocity")) else (b.z_velocity if "z_velocity" in b else 0.0)
                            zv += 800.0
                            if "z_velocity" in b:
                                b.z_velocity = zv
                            elif b.has_method("set_meta"):
                                b.set_meta("z_velocity", zv)

                            var immune = false
                            if b.has_method("get_meta"):
                                immune = b.get_meta("weather_immunity_timer", 0.0) > 0.0 if b.has_meta("weather_immunity_timer") else (b.weather_immunity_timer > 0.0 if "weather_immunity_timer" in b else false)
                            elif "weather_immunity_timer" in b:
                                immune = b.weather_immunity_timer > 0.0

                            if not immune:
                                if "burn_timer" in b:
                                    b.burn_timer += 5.0
                                elif b.has_method("set_meta"):
                                    var current_burn = b.get_meta("burn_timer") if b.has_meta("burn_timer") else 0.0
                                    b.set_meta("burn_timer", current_burn + 5.0)
        else:
            new_eruptions.append(e)
            # Only warn once when it spawns
            if e["timer"] == delta and world.has_method("add_event"):
                world.add_event("lava_warning", {"x": e["x"], "y": e["y"], "radius": e["radius"]})
    eruptions = new_eruptions

    var new_puddles = []
    for p in puddles:
        p["timer"] += delta
        if p["timer"] < p["duration"]:
            new_puddles.append(p)
            for b in balls:
                var is_alive = b.get("alive") if typeof(b) == TYPE_DICTIONARY else (b.alive if "alive" in b else true)
                if is_alive:
                    var bx = b.get("x") if typeof(b) == TYPE_DICTIONARY else b.x
                    var by = b.get("y") if typeof(b) == TYPE_DICTIONARY else b.y

                    var dx = bx - p["x"]
                    var dy = by - p["y"]
                    var dist = sqrt(dx*dx + dy*dy)

                    if dist <= p["radius"]:
                        var dmg = 25.0 * delta
                        if typeof(b) == TYPE_DICTIONARY:
                            b["hp"] -= dmg
                            var immune = b.get("weather_immunity_timer", 0.0) > 0.0
                            if not immune:
                                b["burn_timer"] = b.get("burn_timer", 0.0) + delta
                            if b["hp"] <= 0:
                                b["hp"] = 0
                                b["alive"] = false
                        else:
                            if b.has_method("take_damage"):
                                b.take_damage(dmg)
                            else:
                                b.hp -= dmg

                            var immune = false
                            if b.has_method("get_meta"):
                                immune = b.get_meta("weather_immunity_timer", 0.0) > 0.0 if b.has_meta("weather_immunity_timer") else (b.weather_immunity_timer > 0.0 if "weather_immunity_timer" in b else false)
                            elif "weather_immunity_timer" in b:
                                immune = b.weather_immunity_timer > 0.0

                            if not immune:
                                if "burn_timer" in b:
                                    b.burn_timer += delta
                                elif b.has_method("set_meta"):
                                    var current_burn = b.get_meta("burn_timer") if b.has_meta("burn_timer") else 0.0
                                    b.set_meta("burn_timer", current_burn + delta)

                            if b.hp <= 0:
                                b.hp = 0
                                b.alive = false
    puddles = new_puddles
