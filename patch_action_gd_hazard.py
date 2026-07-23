import re

file_path = "src/ai/action.gd"
with open(file_path, "r") as f:
    content = f.read()

hazard_logic = """                elif hazard.kind == "sticky_mud_puddle":
                    var current_tick = world.tick if "tick" in world else 0
                    var last_updated = -1
                    if typeof(hazard) == TYPE_OBJECT and hazard.has_method("has_meta") and hazard.has_meta("last_updated_tick"): last_updated = hazard.get_meta("last_updated_tick")
                    elif "last_updated_tick" in hazard: last_updated = hazard.last_updated_tick

                    if last_updated != current_tick:
                        if typeof(hazard) == TYPE_OBJECT and hazard.has_method("set_meta"): hazard.set_meta("last_updated_tick", current_tick)
                        elif "last_updated_tick" in hazard: hazard.last_updated_tick = current_tick

                        var h_dur = 10.0
                        if typeof(hazard) == TYPE_OBJECT and hazard.has_method("has_meta") and hazard.has_meta("duration"): h_dur = hazard.get_meta("duration")
                        elif "duration" in hazard: h_dur = hazard.duration

                        h_dur -= delta

                        if typeof(hazard) == TYPE_OBJECT and hazard.has_method("set_meta"): hazard.set_meta("duration", h_dur)
                        elif "duration" in hazard: hazard.duration = h_dur

                        if h_dur <= 0:
                            if typeof(hazard) == TYPE_OBJECT and hazard.has_method("set_meta"): hazard.set_meta("active", false)
                            elif "active" in hazard: hazard.active = false
                        else:
                            for b in world.balls:
                                var b_alive = true
                                if typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")
                                elif typeof(b) == TYPE_DICTIONARY and b.has("alive"): b_alive = b["alive"]
                                elif typeof(b) == TYPE_OBJECT and "alive" in b: b_alive = b.alive

                                if b_alive:
                                    var hx = hazard.x if "x" in hazard else 0.0
                                    var hy = hazard.y if "y" in hazard else 0.0
                                    var bx = 0.0
                                    var by = 0.0
                                    if typeof(b) == TYPE_OBJECT and b.has_method("has_meta"):
                                        bx = b.get_meta("x") if b.has_meta("x") else 0.0
                                        by = b.get_meta("y") if b.has_meta("y") else 0.0
                                    elif typeof(b) == TYPE_OBJECT and "x" in b:
                                        bx = b.x
                                        by = b.y
                                    elif typeof(b) == TYPE_DICTIONARY and b.has("x"):
                                        bx = b["x"]
                                        by = b["y"]

                                    var dist_sq = pow(hx - bx, 2) + pow(hy - by, 2)
                                    var rad_sum = hazard.radius + (b.radius if "radius" in b else 20.0)
                                    if dist_sq < rad_sum * rad_sum:
                                        if typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
                                            b.set_meta("mud_debuff_timer", 3.0)
                                            var stack_cd = b.get_meta("mud_stack_cooldown") if b.has_meta("mud_stack_cooldown") else 0.0
                                            if stack_cd <= 0:
                                                var stacks = b.get_meta("mud_debuff_stacks") if b.has_meta("mud_debuff_stacks") else 0
                                                b.set_meta("mud_debuff_stacks", min(stacks + 1, 5))
                                                b.set_meta("mud_stack_cooldown", 0.5)
                                            else:
                                                b.set_meta("mud_stack_cooldown", stack_cd - delta)
                                        elif "mud_debuff_timer" in b:
                                            b.mud_debuff_timer = 3.0
                                            var stack_cd = b.mud_stack_cooldown if "mud_stack_cooldown" in b else 0.0
                                            if stack_cd <= 0:
                                                var stacks = b.mud_debuff_stacks if "mud_debuff_stacks" in b else 0
                                                b.mud_debuff_stacks = min(stacks + 1, 5)
                                                b.mud_stack_cooldown = 0.5
                                            else:
                                                b.mud_stack_cooldown = stack_cd - delta"""

new_hazard_logic = """                elif hazard.kind == "proximity_mud_puddle":
                    var current_tick = world.tick if "tick" in world else 0
                    var last_updated = -1
                    if typeof(hazard) == TYPE_OBJECT and hazard.has_method("has_meta") and hazard.has_meta("last_updated_tick"): last_updated = hazard.get_meta("last_updated_tick")
                    elif "last_updated_tick" in hazard: last_updated = hazard.last_updated_tick

                    if last_updated != current_tick:
                        if typeof(hazard) == TYPE_OBJECT and hazard.has_method("set_meta"): hazard.set_meta("last_updated_tick", current_tick)
                        elif "last_updated_tick" in hazard: hazard.last_updated_tick = current_tick

                        var h_dur = 30.0
                        if typeof(hazard) == TYPE_OBJECT and hazard.has_method("has_meta") and hazard.has_meta("duration"): h_dur = hazard.get_meta("duration")
                        elif "duration" in hazard: h_dur = hazard.duration

                        h_dur -= delta

                        if typeof(hazard) == TYPE_OBJECT and hazard.has_method("set_meta"): hazard.set_meta("duration", h_dur)
                        elif "duration" in hazard: hazard.duration = h_dur

                        if h_dur <= 0:
                            if typeof(hazard) == TYPE_OBJECT and hazard.has_method("set_meta"): hazard.set_meta("active", false)
                            elif "active" in hazard: hazard.active = false
                        else:
                            var hx = hazard.x if "x" in hazard else 0.0
                            var hy = hazard.y if "y" in hazard else 0.0

                            var triggered = false
                            var trigger_radius = 40.0
                            var owner_id = null
                            if typeof(hazard) == TYPE_OBJECT and hazard.has_method("has_meta") and hazard.has_meta("owner_id"): owner_id = hazard.get_meta("owner_id")
                            elif "owner_id" in hazard: owner_id = hazard.owner_id

                            for b in world.balls:
                                var b_alive = true
                                if typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")
                                elif typeof(b) == TYPE_DICTIONARY and b.has("alive"): b_alive = b["alive"]
                                elif typeof(b) == TYPE_OBJECT and "alive" in b: b_alive = b.alive

                                var b_id = null
                                if typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("id"): b_id = b.get_meta("id")
                                elif typeof(b) == TYPE_DICTIONARY and b.has("id"): b_id = b["id"]
                                elif typeof(b) == TYPE_OBJECT and "id" in b: b_id = b.id

                                if b_alive and b_id != owner_id:
                                    var bx = 0.0
                                    var by = 0.0
                                    if typeof(b) == TYPE_OBJECT and b.has_method("has_meta"):
                                        bx = b.get_meta("x") if b.has_meta("x") else 0.0
                                        by = b.get_meta("y") if b.has_meta("y") else 0.0
                                    elif typeof(b) == TYPE_OBJECT and "x" in b:
                                        bx = b.x
                                        by = b.y
                                    elif typeof(b) == TYPE_DICTIONARY and b.has("x"):
                                        bx = b["x"]
                                        by = b["y"]

                                    var dist_sq = pow(hx - bx, 2) + pow(hy - by, 2)
                                    if dist_sq <= trigger_radius * trigger_radius:
                                        triggered = true
                                        break

                            if triggered:
                                if typeof(hazard) == TYPE_OBJECT and hazard.has_method("set_meta"): hazard.set_meta("active", false)
                                elif "active" in hazard: hazard.active = false

                                for b in world.balls:
                                    var b_alive = true
                                    if typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")
                                    elif typeof(b) == TYPE_DICTIONARY and b.has("alive"): b_alive = b["alive"]
                                    elif typeof(b) == TYPE_OBJECT and "alive" in b: b_alive = b.alive

                                    if b_alive:
                                        var bx = 0.0
                                        var by = 0.0
                                        if typeof(b) == TYPE_OBJECT and b.has_method("has_meta"):
                                            bx = b.get_meta("x") if b.has_meta("x") else 0.0
                                            by = b.get_meta("y") if b.has_meta("y") else 0.0
                                        elif typeof(b) == TYPE_OBJECT and "x" in b:
                                            bx = b.x
                                            by = b.y
                                        elif typeof(b) == TYPE_DICTIONARY and b.has("x"):
                                            bx = b["x"]
                                            by = b["y"]

                                        var dist_sq = pow(hx - bx, 2) + pow(hy - by, 2)
                                        var h_rad = 60.0
                                        if "radius" in hazard: h_rad = hazard.radius
                                        elif typeof(hazard) == TYPE_OBJECT and hazard.has_method("has_meta") and hazard.has_meta("radius"): h_rad = hazard.get_meta("radius")

                                        var rad_sum = h_rad + (b.radius if "radius" in b else 20.0)
                                        if dist_sq <= rad_sum * rad_sum:
                                            if typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
                                                b.set_meta("mud_debuff_timer", 5.0)
                                                b.set_meta("mud_debuff_stacks", 5)
                                                b.set_meta("mud_stack_cooldown", 1.0)
                                            elif "mud_debuff_timer" in b:
                                                b.mud_debuff_timer = 5.0
                                                b.mud_debuff_stacks = 5
                                                b.mud_stack_cooldown = 1.0
""" + "\n" + hazard_logic

content = content.replace(hazard_logic, new_hazard_logic)

with open(file_path, "w") as f:
    f.write(content)
