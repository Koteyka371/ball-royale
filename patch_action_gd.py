import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

gd_replace1 = '''                if self.world != null and self.world.has_method("_collect_booster"):
                    self.world._collect_booster(self.ball, nearest)'''

gd_patch1 = '''                var is_cursed = false
                if self.world != null and "mode" in self.world:
                    if typeof(self.world.mode) == TYPE_OBJECT and "name" in self.world.mode and self.world.mode.name == "Cursed Boosters":
                        is_cursed = true
                    elif typeof(self.world.mode) == TYPE_DICTIONARY and self.world.mode.has("name") and self.world.mode["name"] == "Cursed Boosters":
                        is_cursed = true

                var pre_hp = 100.0
                var pre_speed = 100.0
                var pre_damage = 10.0
                var pre_stamina = 100.0

                if is_cursed:
                    if typeof(self.ball) == TYPE_OBJECT:
                        if "hp" in self.ball: pre_hp = self.ball.hp
                        if "speed" in self.ball: pre_speed = self.ball.speed
                        if "damage" in self.ball: pre_damage = self.ball.damage
                        if "stamina" in self.ball: pre_stamina = self.ball.stamina
                    elif typeof(self.ball) == TYPE_DICTIONARY:
                        if self.ball.has("hp"): pre_hp = self.ball["hp"]
                        if self.ball.has("speed"): pre_speed = self.ball["speed"]
                        if self.ball.has("damage"): pre_damage = self.ball["damage"]
                        if self.ball.has("stamina"): pre_stamina = self.ball["stamina"]

                if self.world != null and self.world.has_method("_collect_booster"):
                    self.world._collect_booster(self.ball, nearest)

                if is_cursed:
                    var post_hp = 100.0
                    var post_speed = 100.0
                    var post_damage = 10.0
                    var post_stamina = 100.0
                    if typeof(self.ball) == TYPE_OBJECT:
                        if "hp" in self.ball: post_hp = self.ball.hp
                        if "speed" in self.ball: post_speed = self.ball.speed
                        if "damage" in self.ball: post_damage = self.ball.damage
                        if "stamina" in self.ball: post_stamina = self.ball.stamina
                    elif typeof(self.ball) == TYPE_DICTIONARY:
                        if self.ball.has("hp"): post_hp = self.ball["hp"]
                        if self.ball.has("speed"): post_speed = self.ball["speed"]
                        if self.ball.has("damage"): post_damage = self.ball["damage"]
                        if self.ball.has("stamina"): post_stamina = self.ball["stamina"]

                    if post_hp > pre_hp:
                        var diff = post_hp - pre_hp
                        if typeof(self.ball) == TYPE_OBJECT: self.ball.hp = pre_hp - diff
                        else: self.ball["hp"] = pre_hp - diff

                    if post_speed > pre_speed:
                        var diff = post_speed - pre_speed
                        if typeof(self.ball) == TYPE_OBJECT:
                            self.ball.speed = pre_speed - diff
                            if "slow_timer" in self.ball: self.ball.slow_timer = 5.0
                            elif self.ball.has_method("set_meta"): self.ball.set_meta("slow_timer", 5.0)
                        else:
                            self.ball["speed"] = pre_speed - diff
                            self.ball["slow_timer"] = 5.0

                    if post_damage > pre_damage:
                        var diff = post_damage - pre_damage
                        if typeof(self.ball) == TYPE_OBJECT: self.ball.damage = pre_damage - diff
                        else: self.ball["damage"] = pre_damage - diff

                    if post_stamina > pre_stamina:
                        var diff = post_stamina - pre_stamina
                        if typeof(self.ball) == TYPE_OBJECT: self.ball.stamina = pre_stamina - diff
                        else: self.ball["stamina"] = pre_stamina - diff'''

gd_replace2 = '''                if self.world != null and self.world.has_method("_collect_booster"):
                    self.world._collect_booster(self.ball, target_item)'''

gd_patch2 = gd_patch1.replace("nearest", "target_item")

content = content.replace(gd_replace1, gd_patch1)
content = content.replace(gd_replace2, gd_patch2)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
