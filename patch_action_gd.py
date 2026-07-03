import re

with open("src/ai/action.gd", "r") as f:
    gd_content = f.read()

# 1. Add _collect_booster logic for disruptor_booster
booster_logic = """            elif "kind" in nearest and nearest.kind == "disruptor_booster":
                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                    self.ball.set_meta("disruptor_aura_timer", 5.0)
                else:
                    self.ball["disruptor_aura_timer"] = 5.0
                if "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
                if "boosters" in world:
                    var idx = world.boosters.find(nearest)
                    if idx != -1:
                        world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "vision_booster":"""
gd_content = gd_content.replace('            elif "kind" in nearest and nearest.kind == "vision_booster":', booster_logic)

# 2. Add update_skill_timer logic
timer_logic = """func _update_skill_timer(delta: float):
    var da_timer = 0.0
    if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("disruptor_aura_timer"):
        da_timer = float(self.ball.get_meta("disruptor_aura_timer"))
    elif "disruptor_aura_timer" in self.ball:
        da_timer = float(self.ball.disruptor_aura_timer)

    if da_timer > 0.0:
        da_timer -= delta
        if da_timer < 0.0: da_timer = 0.0
        if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
            self.ball.set_meta("disruptor_aura_timer", da_timer)
        else:
            self.ball["disruptor_aura_timer"] = da_timer

        if "balls" in world:
            var my_team = ""
            if "team" in self.ball: my_team = self.ball.team
            elif "ball_type" in self.ball: my_team = self.ball.ball_type

            var my_id = -1
            if "id" in self.ball: my_id = self.ball.id
            elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("id"): my_id = self.ball.get_meta("id")

            for other in world.balls:
                var o_alive = true
                if "alive" in other: o_alive = other.alive
                elif typeof(other) != TYPE_DICTIONARY and other.has_method("has_meta") and other.has_meta("alive"): o_alive = other.get_meta("alive")

                var o_id = -1
                if "id" in other: o_id = other.id
                elif typeof(other) != TYPE_DICTIONARY and other.has_method("has_meta") and other.has_meta("id"): o_id = other.get_meta("id")

                if o_alive and o_id != my_id:
                    var o_team = ""
                    if "team" in other: o_team = other.team
                    elif "ball_type" in other: o_team = other.ball_type

                    if o_team != my_team:
                        var dx = self.ball.x - other.x
                        var dy = self.ball.y - other.y
                        if (dx*dx + dy*dy) <= 22500.0:
                            if typeof(other) != TYPE_DICTIONARY and other.has_method("set_meta"):
                                other.set_meta("aura_disruption_timer", 0.5)
                            else:
                                other["aura_disruption_timer"] = 0.5

    var ad_timer = 0.0
    if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("aura_disruption_timer"):
        ad_timer = float(self.ball.get_meta("aura_disruption_timer"))
    elif "aura_disruption_timer" in self.ball:
        ad_timer = float(self.ball.aura_disruption_timer)

    if ad_timer > 0.0:
        ad_timer -= delta
        if ad_timer < 0.0: ad_timer = 0.0
        if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
            self.ball.set_meta("aura_disruption_timer", ad_timer)
        else:
            self.ball["aura_disruption_timer"] = ad_timer

"""
gd_content = gd_content.replace('func _update_skill_timer(delta: float):\n', timer_logic)

# 3. Add aura logic
aura_logic = """    # Determine aura properties
    var aura_radius = 150.0
    var ad_timer = 0.0
    if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("aura_disruption_timer"):
        ad_timer = float(self.ball.get_meta("aura_disruption_timer"))
    elif "aura_disruption_timer" in self.ball:
        ad_timer = float(self.ball.aura_disruption_timer)
    if ad_timer > 0.0:
        aura_radius = 0.0

    # Check nearby friendly balls"""
gd_content = gd_content.replace('    # Determine aura properties\n    var aura_radius = 150.0\n\n    # Check nearby friendly balls', aura_logic)

# 4. Add to ignore lists
gd_content = gd_content.replace('"anchor_booster"]:', '"anchor_booster", "disruptor_booster"]:')


with open("src/ai/action.gd", "w") as f:
    f.write(gd_content)

print("action.gd patched")
