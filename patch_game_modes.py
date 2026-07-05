import re

with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

# 1. Add final_boss_spawned
content = content.replace(
    'self.sudden_death_black_hole_spawned = False',
    'self.sudden_death_black_hole_spawned = False\n        self.final_boss_spawned = False'
)

# 2. Add boss logic right after the decoy spawner logic
boss_logic = """

        # Final Zone Boss logic
        if self.zone_radius <= 250.0 and not getattr(self, "final_boss_spawned", False):
            self.final_boss_spawned = True

            boss_type = "juggernaut"
            if self.weather in ["snow", "blizzard"]:
                boss_type = "yeti"
            elif self.weather == "sandstorm":
                boss_type = "sandworm"

            class FinalBoss:
                def __init__(self, id_val, x, y, b_type):
                    self.id = id_val
                    self.x = x
                    self.y = y
                    self.vx = 0.0
                    self.vy = 0.0
                    self.radius = 40.0
                    self.hp = 3000.0
                    self.max_hp = 3000.0
                    self.alive = True
                    self.ball_type = b_type
                    self.team = "Boss"
                    self.speed = 120.0
                    self.base_speed = 120.0
                    self.damage = 40.0
                    self.base_damage = 40.0
                    self.perception_radius = 500.0
                    self.base_perception_radius = 500.0
                    self.is_final_boss = True
                    self.reward_given = False

            boss_id = 90000 + getattr(self, "random", __import__("random")).randint(0, 9999)
            new_boss = FinalBoss(boss_id, self.zone_x, self.zone_y, boss_type)

            if hasattr(world, "balls"):
                world.balls.append(new_boss)
                if hasattr(world, "entities") and world.balls is not world.entities:
                    world.entities.append(new_boss)

            if hasattr(world, "add_event"):
                world.add_event("final_boss_spawn", {"message": f"A massive {boss_type.capitalize()} has emerged in the center of the safe zone!"})

        # Check boss death
        for b in balls:
            if getattr(b, "is_final_boss", False):
                if not getattr(b, "alive", False) and not getattr(b, "reward_given", False):
                    b.reward_given = True
                    killer_id = getattr(b, "killer_id", None)
                    if hasattr(world, "add_event"):
                        world.add_event("boss_defeated", {"killer_id": killer_id, "points": 5000, "message": f"The final boss was defeated!"})
"""

content = content.replace(
    '# Handle decoy movement mimicking',
    boss_logic + '\n        # Handle decoy movement mimicking'
)

with open("src/ai/game_modes.py", "w") as f:
    f.write(content)
