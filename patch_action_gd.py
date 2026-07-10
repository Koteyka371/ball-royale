with open("src/ai/action.gd", "r") as f:
    content = f.read()

# 1. Patch _attempt_damage for anomaly
attempt_damage_gd_patch = """
        if is_ranged_attack:
            var gm = null
            if typeof(world) == TYPE_DICTIONARY and world.has("game_mode"):
                gm = world.game_mode
            elif typeof(world) != TYPE_DICTIONARY and "game_mode" in world:
                gm = world.game_mode

            var gm_name = ""
            if typeof(gm) == TYPE_DICTIONARY and gm.has("name"): gm_name = gm.name
            elif gm != null and "name" in gm: gm_name = gm.name

            var event_active = false
            if typeof(gm) == TYPE_DICTIONARY and gm.has("event_active"): event_active = gm.event_active
            elif gm != null and "event_active" in gm: event_active = gm.event_active

            if gm_name == "Physics Anomaly Event" and event_active:
                var is_resuming = false
                if typeof(attacker) == TYPE_DICTIONARY and attacker.has("_is_resuming_projectile"):
                    is_resuming = attacker["_is_resuming_projectile"]
                elif typeof(attacker) != TYPE_DICTIONARY and attacker.has_method("has_meta") and attacker.has_meta("_is_resuming_projectile"):
                    is_resuming = attacker.get_meta("_is_resuming_projectile")
                elif typeof(attacker) != TYPE_DICTIONARY and "_is_resuming_projectile" in attacker:
                    is_resuming = attacker._is_resuming_projectile

                if not is_resuming:
                    var t_x = 0.0
                    var t_y = 0.0
                    if typeof(target) == TYPE_DICTIONARY:
                        if target.has("x"): t_x = target.x
                        if target.has("y"): t_y = target.y
                    else:
                        if "x" in target: t_x = target.x
                        if "y" in target: t_y = target.y

                    var a_x = 0.0
                    var a_y = 0.0
                    if typeof(attacker) == TYPE_DICTIONARY:
                        if attacker.has("x"): a_x = attacker.x
                        if attacker.has("y"): a_y = attacker.y
                    else:
                        if "x" in attacker: a_x = attacker.x
                        if "y" in attacker: a_y = attacker.y

                    var dx = t_x - a_x
                    var dy = t_y - a_y
                    var cur_dist = sqrt(dx*dx + dy*dy)
                    var vx = 0.0
                    var vy = 0.0
                    if cur_dist > 0.01:
                        vx = (dx / cur_dist) * 800.0
                        vy = (dy / cur_dist) * 800.0

                    var sus_proj = []
                    if typeof(attacker) == TYPE_DICTIONARY and attacker.has("suspended_projectiles"):
                        sus_proj = attacker["suspended_projectiles"]
                    elif typeof(attacker) != TYPE_DICTIONARY and attacker.has_method("has_meta") and attacker.has_meta("suspended_projectiles"):
                        sus_proj = attacker.get_meta("suspended_projectiles")
                    elif typeof(attacker) != TYPE_DICTIONARY and "suspended_projectiles" in attacker:
                        sus_proj = attacker.suspended_projectiles

                    sus_proj.append({
                        "target": target,
                        "timer": 3.0,
                        "x": a_x,
                        "y": a_y,
                        "vx": vx,
                        "vy": vy,
                        "is_anomaly": true
                    })

                    if typeof(attacker) == TYPE_DICTIONARY:
                        attacker["suspended_projectiles"] = sus_proj
                    elif typeof(attacker) != TYPE_DICTIONARY and attacker.has_method("set_meta"):
                        attacker.set_meta("suspended_projectiles", sus_proj)
                    elif typeof(attacker) != TYPE_DICTIONARY and "suspended_projectiles" in attacker:
                        attacker.suspended_projectiles = sus_proj

                    return

            if "arena" in world and world.arena != null:
"""

content = content.replace("""
        if is_ranged_attack:
            if "arena" in world and world.arena != null:
""", attempt_damage_gd_patch)


# 2. Patch execute for suspended projectiles
execute_suspend_gd_patch = """
    var sus_proj = []
    if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("suspended_projectiles"):
        sus_proj = self.ball["suspended_projectiles"]
    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("suspended_projectiles"):
        sus_proj = self.ball.get_meta("suspended_projectiles")
    elif typeof(self.ball) == TYPE_OBJECT and "suspended_projectiles" in self.ball:
        sus_proj = self.ball.suspended_projectiles

    if sus_proj.size() > 0:
        var updated_proj = []
        var gm = null
        if typeof(self.world) == TYPE_DICTIONARY and self.world.has("game_mode"):
            gm = self.world.game_mode
        elif typeof(self.world) != TYPE_DICTIONARY and "game_mode" in self.world:
            gm = self.world.game_mode

        var cx = 500.0
        var cy = 500.0
        if gm != null:
            var gm_name = ""
            if typeof(gm) == TYPE_DICTIONARY and gm.has("name"): gm_name = gm.name
            elif "name" in gm: gm_name = gm.name
            if gm_name == "Physics Anomaly Event":
                if typeof(gm) == TYPE_DICTIONARY and gm.has("cx"): cx = gm.cx
                elif "cx" in gm: cx = gm.cx
                if typeof(gm) == TYPE_DICTIONARY and gm.has("cy"): cy = gm.cy
                elif "cy" in gm: cy = gm.cy

        for sp in sus_proj:
            sp["timer"] -= delta
            if sp.has("is_anomaly") and sp["is_anomaly"]:
                sp["x"] += sp.get("vx", 0.0) * delta
                sp["y"] += sp.get("vy", 0.0) * delta

                var dx = cx - sp["x"]
                var dy = cy - sp["y"]
                var dist = sqrt(dx*dx + dy*dy)
                if dist > 0.01:
                    var ndx = dx / dist
                    var ndy = dy / dist
                    var tx = -ndy
                    var ty = ndx
                    var force_mag = 400.0 * delta
                    sp["vx"] = sp.get("vx", 0.0) + tx * force_mag
                    sp["vy"] = sp.get("vy", 0.0) + ty * force_mag

                    var target = sp["target"]
                    var t_x = 0.0
                    var t_y = 0.0
                    var t_alive = true
                    var t_hp = 0.0
                    var t_rad = 10.0
                    if typeof(target) == TYPE_DICTIONARY:
                        if target.has("x"): t_x = target.x
                        if target.has("y"): t_y = target.y
                        if target.has("alive"): t_alive = target.alive
                        if target.has("hp"): t_hp = target.hp
                        if target.has("radius"): t_rad = target.radius
                    else:
                        if "x" in target: t_x = target.x
                        if "y" in target: t_y = target.y
                        if "alive" in target: t_alive = target.alive
                        if "hp" in target: t_hp = target.hp
                        if "radius" in target: t_rad = target.radius

                    var tdx = t_x - sp["x"]
                    var tdy = t_y - sp["y"]
                    var tdist = sqrt(tdx*tdx + tdy*tdy)

                    if tdist <= (t_rad + 20.0):
                        if t_alive or t_hp > 0:
                            if typeof(self.ball) == TYPE_DICTIONARY:
                                self.ball["_is_resuming_projectile"] = true
                            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                self.ball.set_meta("_is_resuming_projectile", true)
                            elif typeof(self.ball) == TYPE_OBJECT and "_is_resuming_projectile" in self.ball:
                                self.ball._is_resuming_projectile = true

                            self._attempt_damage(self.ball, target)

                            if typeof(self.ball) == TYPE_DICTIONARY:
                                self.ball["_is_resuming_projectile"] = false
                            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                self.ball.set_meta("_is_resuming_projectile", false)
                            elif typeof(self.ball) == TYPE_OBJECT and "_is_resuming_projectile" in self.ball:
                                self.ball._is_resuming_projectile = false
                        continue

            if sp["timer"] <= 0:
                if not (sp.has("is_anomaly") and sp["is_anomaly"]):
                    var t_alive = true
                    var t_hp = 0.0
                    if typeof(sp["target"]) == TYPE_DICTIONARY:
                        if sp["target"].has("alive"): t_alive = sp["target"].alive
                        if sp["target"].has("hp"): t_hp = sp["target"].hp
                    else:
                        if "alive" in sp["target"]: t_alive = sp["target"].alive
                        if "hp" in sp["target"]: t_hp = sp["target"].hp
                    if t_alive or t_hp > 0:
                        if typeof(self.ball) == TYPE_DICTIONARY:
                            self.ball["_is_resuming_projectile"] = true
                        elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                            self.ball.set_meta("_is_resuming_projectile", true)
                        elif typeof(self.ball) == TYPE_OBJECT and "_is_resuming_projectile" in self.ball:
                            self.ball._is_resuming_projectile = true

                        self._attempt_damage(self.ball, sp["target"])

                        if typeof(self.ball) == TYPE_DICTIONARY:
                            self.ball["_is_resuming_projectile"] = false
                        elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                            self.ball.set_meta("_is_resuming_projectile", false)
                        elif typeof(self.ball) == TYPE_OBJECT and "_is_resuming_projectile" in self.ball:
                            self.ball._is_resuming_projectile = false
            else:
                updated_proj.append(sp)

        if typeof(self.ball) == TYPE_DICTIONARY:
            self.ball["suspended_projectiles"] = updated_proj
        elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("suspended_projectiles", updated_proj)
        elif typeof(self.ball) == TYPE_OBJECT and "suspended_projectiles" in self.ball:
            self.ball.suspended_projectiles = updated_proj
"""

old_suspend_gd_logic = """
    var sus_proj = []
    if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("suspended_projectiles"):
        sus_proj = self.ball["suspended_projectiles"]
    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("suspended_projectiles"):
        sus_proj = self.ball.get_meta("suspended_projectiles")
    elif typeof(self.ball) == TYPE_OBJECT and "suspended_projectiles" in self.ball:
        sus_proj = self.ball.suspended_projectiles

    if sus_proj.size() > 0:
        var updated_proj = []
        for sp in sus_proj:
            sp["timer"] -= delta
            if sp["timer"] <= 0:
                var t_alive = true
                var t_hp = 0.0
                if typeof(sp["target"]) == TYPE_DICTIONARY:
                    if sp["target"].has("alive"):
                        t_alive = sp["target"].alive
                    if sp["target"].has("hp"):
                        t_hp = sp["target"].hp
                else:
                    if "alive" in sp["target"]:
                        t_alive = sp["target"].alive
                    if "hp" in sp["target"]:
                        t_hp = sp["target"].hp
                if t_alive or t_hp > 0:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["_is_resuming_projectile"] = true
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                        self.ball.set_meta("_is_resuming_projectile", true)
                    elif typeof(self.ball) == TYPE_OBJECT and "_is_resuming_projectile" in self.ball:
                        self.ball._is_resuming_projectile = true

                    self._attempt_damage(self.ball, sp["target"])

                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["_is_resuming_projectile"] = false
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                        self.ball.set_meta("_is_resuming_projectile", false)
                    elif typeof(self.ball) == TYPE_OBJECT and "_is_resuming_projectile" in self.ball:
                        self.ball._is_resuming_projectile = false
            else:
                updated_proj.append(sp)

        if typeof(self.ball) == TYPE_DICTIONARY:
            self.ball["suspended_projectiles"] = updated_proj
        elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("suspended_projectiles", updated_proj)
        elif typeof(self.ball) == TYPE_OBJECT and "suspended_projectiles" in self.ball:
            self.ball.suspended_projectiles = updated_proj
"""

content = content.replace(old_suspend_gd_logic.strip(), execute_suspend_gd_patch.strip())


# 3. Patch execute at the end for physics_anomaly_speed_mod
speed_mod_gd_patch = """
    var speed_mod = 1.0
    if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("physics_anomaly_speed_mod"):
        speed_mod = self.ball["physics_anomaly_speed_mod"]
    elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("physics_anomaly_speed_mod"):
        speed_mod = self.ball.get_meta("physics_anomaly_speed_mod")
    elif typeof(self.ball) != TYPE_DICTIONARY and "physics_anomaly_speed_mod" in self.ball:
        speed_mod = self.ball.physics_anomaly_speed_mod

    if speed_mod != 1.0:
        if typeof(self.ball) == TYPE_DICTIONARY:
            if self.ball.has("vx"): self.ball["vx"] *= speed_mod
            if self.ball.has("vy"): self.ball["vy"] *= speed_mod
        else:
            if "vx" in self.ball: self.ball.vx *= speed_mod
            if "vy" in self.ball: self.ball.vy *= speed_mod

    # Cleanup temporary reflections
"""

content = content.replace("    # Cleanup temporary reflections", speed_mod_gd_patch)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
print("action.gd patched")
