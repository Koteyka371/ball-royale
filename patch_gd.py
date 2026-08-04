import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

eval_block = """            elif h_kind == "deployable_fake_weather_station":
                var current_tick = 0
                if world != null and "tick" in world: current_tick = world.tick

                var last_updated = -1
                if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("last_updated_tick"):
                    last_updated = hazard.get_meta("last_updated_tick")
                elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("last_updated_tick"):
                    last_updated = hazard["last_updated_tick"]

                if last_updated != current_tick:
                    if typeof(hazard) == TYPE_OBJECT:
                        hazard.set_meta("last_updated_tick", current_tick)
                    elif typeof(hazard) == TYPE_DICTIONARY:
                        hazard["last_updated_tick"] = current_tick

                    var owner_id = null
                    if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("owner_id"):
                        owner_id = hazard.get_meta("owner_id")
                    elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("owner_id"):
                        owner_id = hazard["owner_id"]

                    var capturers = []
                    if world != null and "balls" in world:
                        for b in world.balls:
                            var b_alive = true
                            if typeof(b) == TYPE_OBJECT and "alive" in b: b_alive = b.alive
                            elif typeof(b) == TYPE_DICTIONARY and b.has("alive"): b_alive = b["alive"]

                            var b_id = null
                            if typeof(b) == TYPE_OBJECT and "id" in b: b_id = b.id
                            elif typeof(b) == TYPE_DICTIONARY and b.has("id"): b_id = b["id"]

                            if b_alive and b_id != owner_id:
                                var bx = 0.0; var by = 0.0
                                if typeof(b) == TYPE_OBJECT: bx = b.x; by = b.y
                                elif typeof(b) == TYPE_DICTIONARY: bx = b["x"]; by = b["y"]

                                var dist_sq = (bx - hazard.x) * (bx - hazard.x) + (by - hazard.y) * (by - hazard.y)
                                var h_rad = 150.0
                                if typeof(hazard) == TYPE_OBJECT and "radius" in hazard: h_rad = hazard.radius
                                elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("radius"): h_rad = hazard["radius"]

                                if dist_sq <= (h_rad * h_rad):
                                    capturers.append(b)

                    if capturers.size() > 0:
                        var progress = 0.0
                        if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("capture_progress"):
                            progress = hazard.get_meta("capture_progress")
                        elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("capture_progress"):
                            progress = hazard["capture_progress"]

                        progress += 20.0 * delta

                        if typeof(hazard) == TYPE_OBJECT:
                            hazard.set_meta("capture_progress", progress)
                        elif typeof(hazard) == TYPE_DICTIONARY:
                            hazard["capture_progress"] = progress

                        if progress >= 100.0:
                            if typeof(hazard) == TYPE_OBJECT:
                                hazard.active = false
                            elif typeof(hazard) == TYPE_DICTIONARY:
                                hazard["active"] = false

                            if world != null and "events" in world:
                                world.events.append({"type": "emp_pulse_hit", "data": {"x": hazard.x, "y": hazard.y, "radius": 250.0}})

                            for b in capturers:
                                if typeof(b) == TYPE_OBJECT:
                                    if "hp" in b:
                                        b.hp -= 30.0
                                        if b.hp <= 0: b.alive = false
                                    if "speed_debuff_timer" in b:
                                        b.speed_debuff_timer = max(b.speed_debuff_timer, 5.0)
                                    elif b.has_method("set"):
                                        b.set("speed_debuff_timer", 5.0)
                                    if "speed_debuff_multiplier" in b:
                                        b.speed_debuff_multiplier = 0.5
                                    elif b.has_method("set"):
                                        b.set("speed_debuff_multiplier", 0.5)
                                elif typeof(b) == TYPE_DICTIONARY:
                                    if b.has("hp"):
                                        b["hp"] -= 30.0
                                        if b["hp"] <= 0: b["alive"] = false
                                    b["speed_debuff_timer"] = 5.0
                                    b["speed_debuff_multiplier"] = 0.5
"""

content = content.replace('            elif h_kind == "deployable_shockwave_mine":', eval_block + '\n            elif h_kind == "deployable_shockwave_mine":')

with open("src/ai/action.gd", "w") as f:
    f.write(content)
