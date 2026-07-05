import re
with open("src/ai/action.gd", "r") as f:
    code = f.read()

new_code = code.replace(
"""    if typeof(my_ball) == TYPE_OBJECT and my_ball.has_method("set_meta"):
        my_ball.set_meta("in_anomaly_zone", in_anomaly_zone)
    elif typeof(my_ball) == TYPE_DICTIONARY:
        my_ball["in_anomaly_zone"] = in_anomaly_zone

    var gm = null
    if world != null and "game_mode" in world:
        gm = world.game_mode
    var is_zero_gravity = false
    if in_anomaly_zone:
        is_zero_gravity = true""",
"""    if typeof(my_ball) == TYPE_OBJECT and my_ball.has_method("set_meta"):
        my_ball.set_meta("in_anomaly_zone", in_anomaly_zone)
    elif typeof(my_ball) == TYPE_DICTIONARY:
        my_ball["in_anomaly_zone"] = in_anomaly_zone

    var in_ice_patch = false
    if world != null and "arena" in world and world.arena != null and "hazards" in world.arena:
        for hazard in world.arena.hazards:
            var kind = ""
            if typeof(hazard) == TYPE_DICTIONARY and hazard.has("kind"): kind = hazard["kind"]
            elif typeof(hazard) == TYPE_OBJECT and "kind" in hazard: kind = hazard.kind

            var active = true
            if typeof(hazard) == TYPE_DICTIONARY and hazard.has("active"): active = hazard["active"]
            elif typeof(hazard) == TYPE_OBJECT and "active" in hazard: active = hazard.active

            if kind == "ice_patch" and active:
                var hx = 0.0
                var hy = 0.0
                var hr = 0.0
                if typeof(hazard) == TYPE_DICTIONARY:
                    if hazard.has("x"): hx = hazard["x"]
                    if hazard.has("y"): hy = hazard["y"]
                    if hazard.has("radius"): hr = hazard["radius"]
                else:
                    if "x" in hazard: hx = hazard.x
                    if "y" in hazard: hy = hazard.y
                    if "radius" in hazard: hr = hazard.radius

                var dx = hx - my_ball.x
                var dy = hy - my_ball.y
                if dx*dx + dy*dy <= hr*hr:
                    in_ice_patch = true
                    break

    if typeof(my_ball) == TYPE_OBJECT and my_ball.has_method("set_meta"):
        my_ball.set_meta("in_ice_patch", in_ice_patch)
    elif typeof(my_ball) == TYPE_DICTIONARY:
        my_ball["in_ice_patch"] = in_ice_patch

    var gm = null
    if world != null and "game_mode" in world:
        gm = world.game_mode
    var is_zero_gravity = false
    if in_anomaly_zone:
        is_zero_gravity = true""")

new_code = new_code.replace(
"""    if is_zero_gravity:
        if "vx" in my_ball and "vy" in my_ball:
            my_ball.vx *= (1.0 - 0.5 * delta)
            my_ball.vy *= (1.0 - 0.5 * delta)
            my_ball.x += my_ball.vx * delta
            my_ball.y += my_ball.vy * delta""",
"""    if is_zero_gravity:
        if "vx" in my_ball and "vy" in my_ball:
            my_ball.vx *= (1.0 - 0.5 * delta)
            my_ball.vy *= (1.0 - 0.5 * delta)
            my_ball.x += my_ball.vx * delta
            my_ball.y += my_ball.vy * delta

    if in_ice_patch:
        if "vx" in my_ball and "vy" in my_ball:
            my_ball.x += my_ball.vx * delta
            my_ball.y += my_ball.vy * delta""")

new_code = new_code.replace(
"""            if in_anomaly_zone:
                knockback_multiplier = 5.0""",
"""            var in_ice_patch_knockback = false
            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("in_ice_patch"):
                in_ice_patch_knockback = self.ball.get_meta("in_ice_patch")
            elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("in_ice_patch"):
                in_ice_patch_knockback = self.ball["in_ice_patch"]

            if in_ice_patch_knockback:
                knockback_multiplier = 2.0
            if in_anomaly_zone:
                knockback_multiplier = 5.0""")

new_code = new_code.replace(
"""            var new_speed = min(speed * 1.5, 2000.0)""",
"""            var in_ice_patch_bounce = false
            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("in_ice_patch"):
                in_ice_patch_bounce = self.ball.get_meta("in_ice_patch")
            elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("in_ice_patch"):
                in_ice_patch_bounce = self.ball["in_ice_patch"]

            var new_speed = min(speed * 1.5, 2000.0)
            if in_ice_patch_bounce:
                new_speed = min(speed * 2.0, 3000.0)""")

with open("src/ai/action.gd", "w") as f:
    f.write(new_code)
