import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

target2 = '''                    if hasattr(self.world, "_collect_booster"):
                        self.world._collect_booster(self.ball, target_item)'''

replacement2 = '''                    is_cursed_mode = hasattr(self.world, "mode") and getattr(self.world.mode, "name", "") == "Cursed Boosters"
                    pre_stats = {}
                    if is_cursed_mode:
                        pre_stats = {
                            "hp": getattr(self.ball, "hp", 100.0),
                            "speed": getattr(self.ball, "speed", 100.0),
                            "damage": getattr(self.ball, "damage", 10.0),
                            "stamina": getattr(self.ball, "stamina", 100.0)
                        }

                    if hasattr(self.world, "_collect_booster"):
                        self.world._collect_booster(self.ball, target_item)

                    if is_cursed_mode:
                        post_hp = getattr(self.ball, "hp", 100.0)
                        if post_hp > pre_stats["hp"]:
                            self.ball.hp = pre_stats["hp"] - (post_hp - pre_stats["hp"])
                        post_speed = getattr(self.ball, "speed", 100.0)
                        if post_speed > pre_stats["speed"]:
                            self.ball.speed = pre_stats["speed"] - (post_speed - pre_stats["speed"])
                            self.ball.slow_timer = getattr(self.ball, "slow_timer", 0.0) + 5.0
                        post_damage = getattr(self.ball, "damage", 10.0)
                        if post_damage > pre_stats["damage"]:
                            self.ball.damage = pre_stats["damage"] - (post_damage - pre_stats["damage"])
                        post_stamina = getattr(self.ball, "stamina", 100.0)
                        if post_stamina > pre_stats["stamina"]:
                            self.ball.stamina = pre_stats["stamina"] - (post_stamina - pre_stats["stamina"])'''

content = content.replace(target2, replacement2)
with open("src/ai/action.py", "w") as f:
    f.write(content)
