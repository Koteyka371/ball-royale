def apply_patch():
    with open("src/ai/action.gd", "r") as f:
        content = f.read()

    target_gd = """    var bounced_col = _resolve_collisions()
    var bounced_wall = _clamp_position()"""

    replacement_gd = """    var bounced_col = _resolve_collisions()
    var bounced_wall = _clamp_position()

    var is_proj = false
    var b_type_curr = ""
    if "ball_type" in self.ball: b_type_curr = self.ball.ball_type
    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("ball_type"): b_type_curr = self.ball.get_meta("ball_type")
    if b_type_curr == "projectile" or b_type_curr == "spell": is_proj = true
    elif "is_projectile" in self.ball and self.ball.is_projectile: is_proj = true

    var o_id = null
    if "owner_id" in self.ball: o_id = self.ball.owner_id
    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("owner_id"): o_id = self.ball.get_meta("owner_id")

    var checked = false
    if "_pinball_checked" in self.ball and self.ball._pinball_checked: checked = true
    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("_pinball_checked"): checked = self.ball.get_meta("_pinball_checked")

    if is_proj and o_id != null and not checked:
        if typeof(self.ball) == TYPE_DICTIONARY: self.ball["_pinball_checked"] = true
        elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("_pinball_checked", true)
        else: self.ball.set("_pinball_checked", true)

        if typeof(self.world) == TYPE_OBJECT and "balls" in self.world:
            var o_ball = null
            for b in self.world.balls:
                var b_id = null
                if "id" in b: b_id = b.id
                elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("id"): b_id = b.get_meta("id")
                if b_id == o_id:
                    var o_alive = true
                    if "alive" in b: o_alive = b.alive
                    if o_alive:
                        o_ball = b
                        break
            if o_ball != null:
                var pinball_timer = 0.0
                if "pinball_projectile_timer" in o_ball: pinball_timer = o_ball.pinball_projectile_timer
                elif typeof(o_ball) == TYPE_OBJECT and o_ball.has_method("get_meta") and o_ball.has_meta("pinball_projectile_timer"): pinball_timer = o_ball.get_meta("pinball_projectile_timer")
                if pinball_timer > 0.0:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["is_ricochet_laser"] = true
                        self.ball["bounces_left"] = 5
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                        self.ball.set_meta("is_ricochet_laser", true)
                        self.ball.set_meta("bounces_left", 5)
                    else:
                        self.ball.set("is_ricochet_laser", true)
                        self.ball.set("bounces_left", 5)
"""

    if target_gd in content:
        content = content.replace(target_gd, replacement_gd)
        print("Patched wall bounce in action.gd")
    else:
        print("Not found")

    with open("src/ai/action.gd", "w") as f:
        f.write(content)
apply_patch()
