import re

with open('src/ai/action.gd', 'r') as f:
    content_gd = f.read()

old_code_gd = """        elif skill_name == "mimic_clone":
            if self.world != null and "balls" in self.world:
                var active_clone = null
                var my_id = -2
                if "id" in self.ball: my_id = self.ball.id
                elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): my_id = self.ball.get_meta("id")

                for b in self.world.balls:
                    var b_is_mimic_clone = false
                    if "is_mimic_clone" in b: b_is_mimic_clone = b.is_mimic_clone
                    elif b.has_method("get_meta") and b.has_meta("is_mimic_clone"): b_is_mimic_clone = b.get_meta("is_mimic_clone")

                    var b_alive = true
                    if "alive" in b: b_alive = b.alive
                    elif b.has_method("get_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")

                    if b_is_mimic_clone and b_alive:
                        var owner = -1
                        if "mimic_owner" in b: owner = b.mimic_owner
                        elif b.has_method("get_meta") and b.has_meta("mimic_owner"): owner = b.get_meta("mimic_owner")

                        if owner == my_id:
                            active_clone = b
                            break

                if active_clone != null:
                    var my_x = 0.0
                    var my_y = 0.0
                    if "x" in self.ball: my_x = float(self.ball.x)
                    if "y" in self.ball: my_y = float(self.ball.y)

                    var clone_x = 0.0
                    var clone_y = 0.0
                    if "x" in active_clone: clone_x = float(active_clone.x)
                    if "y" in active_clone: clone_y = float(active_clone.y)

                    if "x" in self.ball: self.ball.x = clone_x
                    if "y" in self.ball: self.ball.y = clone_y

                    if "x" in active_clone: active_clone.x = my_x
                    if "y" in active_clone: active_clone.y = my_y

                    if "events" in self.world:
                        self.world.events.append({
                            "type": "visual_effect",
                            "data": {"type": "line", "x": my_x, "y": my_y, "tx": clone_x, "ty": clone_y, "color": "purple"}
                        })
                else:"""

new_code_gd = """        elif skill_name == "mimic_clone":
            if self.world != null and "balls" in self.world:
                var active_clone = null
                var my_id = -2
                if "id" in self.ball: my_id = self.ball.id
                elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): my_id = self.ball.get_meta("id")

                for b in self.world.balls:
                    var b_is_mimic_clone = false
                    if "is_mimic_clone" in b: b_is_mimic_clone = b.is_mimic_clone
                    elif b.has_method("get_meta") and b.has_meta("is_mimic_clone"): b_is_mimic_clone = b.get_meta("is_mimic_clone")

                    var b_alive = true
                    if "alive" in b: b_alive = b.alive
                    elif b.has_method("get_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")

                    if b_is_mimic_clone and b_alive:
                        var owner = -1
                        if "mimic_owner" in b: owner = b.mimic_owner
                        elif b.has_method("get_meta") and b.has_meta("mimic_owner"): owner = b.get_meta("mimic_owner")

                        if owner == my_id:
                            active_clone = b
                            break

                if active_clone != null:
                    var has_swapped = false
                    if "has_swapped" in active_clone: has_swapped = active_clone.has_swapped
                    elif active_clone.has_method("get_meta") and active_clone.has_meta("has_swapped"): has_swapped = active_clone.get_meta("has_swapped")

                    if has_swapped:
                        if "hp" in active_clone: active_clone.hp = 0.0
                        if "alive" in active_clone: active_clone.alive = false
                        if active_clone.has_method("set_meta"):
                            active_clone.set_meta("hp", 0.0)
                            active_clone.set_meta("alive", false)
                        var cooldown = 5.0
                        if "SKILL_COOLDOWN" in self.ball: cooldown = float(self.ball.SKILL_COOLDOWN)
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("SKILL_COOLDOWN"): cooldown = float(self.ball.get_meta("SKILL_COOLDOWN"))
                        if "skill_timer" in self.ball: self.ball.skill_timer = cooldown
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("skill_timer", cooldown)
                    else:
                        var my_x = 0.0
                        var my_y = 0.0
                        if "x" in self.ball: my_x = float(self.ball.x)
                        if "y" in self.ball: my_y = float(self.ball.y)

                        var clone_x = 0.0
                        var clone_y = 0.0
                        if "x" in active_clone: clone_x = float(active_clone.x)
                        if "y" in active_clone: clone_y = float(active_clone.y)

                        if "x" in self.ball: self.ball.x = clone_x
                        if "y" in self.ball: self.ball.y = clone_y

                        if "x" in active_clone: active_clone.x = my_x
                        if "y" in active_clone: active_clone.y = my_y

                        if active_clone.has_method("set_meta"):
                            active_clone.set_meta("has_swapped", true)
                        elif "has_swapped" in active_clone:
                            active_clone.has_swapped = true

                        var cooldown = 5.0
                        if "SKILL_COOLDOWN" in self.ball: cooldown = float(self.ball.SKILL_COOLDOWN)
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("SKILL_COOLDOWN"): cooldown = float(self.ball.get_meta("SKILL_COOLDOWN"))
                        if "skill_timer" in self.ball: self.ball.skill_timer = cooldown
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("skill_timer", cooldown)

                        if "events" in self.world:
                            self.world.events.append({
                                "type": "visual_effect",
                                "data": {"type": "line", "x": my_x, "y": my_y, "tx": clone_x, "ty": clone_y, "color": "purple"}
                            })
                else:"""

content_gd = content_gd.replace(old_code_gd, new_code_gd)

with open('src/ai/action.gd', 'w') as f:
    f.write(content_gd)
