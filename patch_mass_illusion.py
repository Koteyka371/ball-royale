import re

with open('src/ai/action.gd', 'r') as f:
    content_gd = f.read()

old_code_gd = """        elif skill_name == "mass_illusion":
            if self.world != null and "balls" in self.world:
                for i in range(3):"""

new_code_gd = """        elif skill_name == "mass_illusion":
            var active_illusions = []
            if "balls" in self.world:
                for b in self.world.balls:
                    var is_i = false
                    if "is_illusion" in b and b.is_illusion:
                        is_i = true
                    elif b.has_method("get_meta") and b.has_meta("is_illusion") and b.get_meta("is_illusion"):
                        is_i = true

                    if is_i:
                        var owner = -1
                        if "mimic_owner" in b: owner = b.mimic_owner
                        elif b.has_method("get_meta") and b.has_meta("mimic_owner"): owner = b.get_meta("mimic_owner")

                        var b_alive = true
                        if "alive" in b: b_alive = b.alive
                        elif b.has_method("get_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")

                        var self_id = -2
                        if "id" in self.ball: self_id = self.ball.id
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): self_id = self.ball.get_meta("id")

                        if owner == self_id and b_alive:
                            active_illusions.append(b)

            if active_illusions.size() > 0:
                for d in active_illusions:
                    if "hp" in d: d.hp = 0.0
                    if "alive" in d: d.alive = false
                    if d.has_method("set_meta"):
                        d.set_meta("hp", 0.0)
                        d.set_meta("alive", false)

                var cooldown = 10.0
                if "SKILL_COOLDOWN" in self.ball: cooldown = float(self.ball.SKILL_COOLDOWN)
                elif self.ball.has_method("get_meta") and self.ball.has_meta("SKILL_COOLDOWN"): cooldown = float(self.ball.get_meta("SKILL_COOLDOWN"))

                if "skill_timer" in self.ball: self.ball.skill_timer = cooldown
                elif self.ball.has_method("set_meta"): self.ball.set_meta("skill_timer", cooldown)
            elif self.world != null and "balls" in self.world:
                for i in range(3):"""

content_gd = content_gd.replace(old_code_gd, new_code_gd)

with open('src/ai/action.gd', 'w') as f:
    f.write(content_gd)
