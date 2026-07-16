import sys

def patch_file():
    with open('src/ai/action.py', 'r') as f:
        content = f.read()

    search = """                            if weather == "thunderstorm":
                                hazard_damage = 20.0 * delta
                                if hasattr(self.ball, "take_damage"):
                                    self.ball.take_damage(hazard_damage, "Shock")
                                elif hasattr(self.ball, "hp"):
                                    self.ball.hp -= hazard_damage
                                    if self.ball.hp <= 0:
                                        self.ball.alive = False

                                # Electrified puddle stalls player for 0.5s due to Shock
                                self.ball.stun_timer = 0.5
                                # Reset speed drastically when shocked
                                self.ball.speed = 0"""

    replace = """                            if weather == "thunderstorm":
                                hazard_damage = 20.0 * delta
                                if hasattr(self.ball, "take_damage"):
                                    self.ball.take_damage(hazard_damage)
                                elif hasattr(self.ball, "hp"):
                                    self.ball.hp -= hazard_damage
                                    if self.ball.hp <= 0:
                                        self.ball.alive = False

                                # Electrified puddle stalls player for 0.5s due to Shock
                                if getattr(self.ball, "shock_cooldown", 0.0) <= 0:
                                    self.ball.stun_timer = 0.5
                                    self.ball.shock_cooldown = 2.0
                                    if hasattr(self.ball, "vx"):
                                        self.ball.vx = 0.0
                                    if hasattr(self.ball, "vy"):
                                        self.ball.vy = 0.0
                                else:
                                    self.ball.shock_cooldown -= delta"""

    if search not in content:
        print("Search string not found in action.py")
        return

    content = content.replace(search, replace)

    with open('src/ai/action.py', 'w') as f:
        f.write(content)

    print("Patched action.py")

patch_file()
