import math

class GuildWarsMode:
    def __init__(self):
        self.name = "Guild Wars"
        self.description = "Attack enemy guild bases while defending your own."
        self.active_defenses = []

    def setup(self, world, balls):
        if hasattr(world, "guild_defenses"):
            for d in world.guild_defenses:
                defense_obj = type("DefenseObj", (object,), {
                    "type": d["type"],
                    "x": d["x"],
                    "y": d["y"],
                    "hp": d["hp"],
                    "max_hp": d.get("max_hp", d["hp"]),
                    "radius": 30 if d["type"] == "turret" else (50 if d["type"] == "wall" else 20),
                    "team": d.get("team", "defender"),
                    "cooldown": 0,
                    "alive": True
                })
                self.active_defenses.append(defense_obj)

    def tick(self, world, balls, delta=0.016):
        # Update defenses
        for d in self.active_defenses:
            if not d.alive: continue

            if d.type == "turret":
                d.cooldown -= delta
                if d.cooldown <= 0:
                    # Find target
                    target = None
                    min_dist = 500
                    for b in balls:
                        if getattr(b, "alive", False) and getattr(b, "team", None) != d.team:
                            dist = math.hypot(b.x - d.x, b.y - d.y)
                            if dist < min_dist:
                                min_dist = dist
                                target = b

                    if target:
                        # Fire (simplification: deal direct damage)
                        if hasattr(target, "take_damage"):
                            target.take_damage(50)
                        else:
                            target.hp -= 50
                            if target.hp <= 0:
                                target.alive = False
                        d.cooldown = 1.0 # 1 second cooldown

            elif d.type == "trap":
                # Check collision with enemies
                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "team", None) != d.team:
                        dist = math.hypot(b.x - d.x, b.y - d.y)
                        if dist < d.radius + getattr(b, "radius", 20):
                            # Trigger trap
                            if hasattr(b, "take_damage"):
                                b.take_damage(200)
                            else:
                                b.hp -= 200
                                if b.hp <= 0:
                                    b.alive = False
                            d.alive = False # Trap consumed
                            break

            elif d.type == "wall":
                # Basic collision handling
                pass

        # Remove dead defenses
        self.active_defenses = [d for d in self.active_defenses if d.alive]

    def apply_dynamic_traits(self, world, balls, delta):
        pass
