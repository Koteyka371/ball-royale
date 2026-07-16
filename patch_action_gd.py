import sys

def patch_file():
    with open('src/ai/action.gd', 'r') as f:
        content = f.read()

    search = """                        if weather == "thunderstorm":
                            var hazard_damage = 20.0 * delta
                            if self.ball.has_method("take_damage"):
                                self.ball.take_damage(hazard_damage, "Shock")
                            elif "hp" in self.ball:
                                self.ball.hp -= hazard_damage
                                if self.ball.hp <= 0:
                                    if "alive" in self.ball: self.ball.alive = false

                            # Electrified puddle stalls player for 0.5s due to Shock
                            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                self.ball.set_meta("stun_timer", 0.5)
                            elif typeof(self.ball) == TYPE_DICTIONARY:
                                self.ball["stun_timer"] = 0.5
                            elif "stun_timer" in self.ball:
                                self.ball.stun_timer = 0.5

                            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                self.ball.set_meta("speed", 0.0)
                            elif typeof(self.ball) == TYPE_DICTIONARY:
                                self.ball["speed"] = 0.0
                            elif "speed" in self.ball:
                                self.ball.speed = 0.0"""

    replace = """                        if weather == "thunderstorm":
                            var hazard_damage = 20.0 * delta
                            if self.ball.has_method("take_damage"):
                                self.ball.take_damage(hazard_damage)
                            elif "hp" in self.ball:
                                self.ball.hp -= hazard_damage
                                if self.ball.hp <= 0:
                                    if "alive" in self.ball: self.ball.alive = false

                            # Electrified puddle stalls player for 0.5s due to Shock
                            var cd = 0.0
                            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
                                cd = self.ball.get_meta("shock_cooldown") if self.ball.has_meta("shock_cooldown") else 0.0
                            elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("shock_cooldown"):
                                cd = self.ball["shock_cooldown"]
                            elif "shock_cooldown" in self.ball:
                                cd = self.ball.shock_cooldown

                            if cd <= 0.0:
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                    self.ball.set_meta("stun_timer", 0.5)
                                    self.ball.set_meta("shock_cooldown", 2.0)
                                    if "vx" in self.ball: self.ball.vx = 0.0
                                    if "vy" in self.ball: self.ball.vy = 0.0
                                elif typeof(self.ball) == TYPE_DICTIONARY:
                                    self.ball["stun_timer"] = 0.5
                                    self.ball["shock_cooldown"] = 2.0
                                    if self.ball.has("vx"): self.ball["vx"] = 0.0
                                    if self.ball.has("vy"): self.ball["vy"] = 0.0
                                elif "stun_timer" in self.ball:
                                    self.ball.stun_timer = 0.5
                                    self.ball.shock_cooldown = 2.0
                                    if "vx" in self.ball: self.ball.vx = 0.0
                                    if "vy" in self.ball: self.ball.vy = 0.0
                            else:
                                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                                    self.ball.set_meta("shock_cooldown", cd - delta)
                                elif typeof(self.ball) == TYPE_DICTIONARY:
                                    self.ball["shock_cooldown"] = cd - delta
                                elif "shock_cooldown" in self.ball:
                                    self.ball.shock_cooldown -= delta"""

    if search not in content:
        print("Search string not found in action.gd")
        return

    content = content.replace(search, replace)

    with open('src/ai/action.gd', 'w') as f:
        f.write(content)

    print("Patched action.gd")

patch_file()
