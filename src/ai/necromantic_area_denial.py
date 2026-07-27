from typing import Any, List
import math

class VolatilePoisonCloud:
    def __init__(self, x: float, y: float, team: str):
        self.x = x
        self.y = y
        self.team = team
        self.radius = 10.0
        self.max_radius = 80.0
        self.growth_rate = 15.0
        self.timer = 5.0
        self.kind = "volatile_poison_cloud"
        self.damage_per_sec = 25.0
        self.explosion_damage = 50.0

class NecromanticAreaDenialMode:
    def __init__(self):
        self.name = "Necromantic Area Denial"
        self.description = "Skill that turns dead enemy remains into volatile poison clouds."

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        if not hasattr(world, "arena"):
            return

        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []

        # Find balls with the necromantic area denial skill activated
        skill_users = [b for b in balls if getattr(b, "alive", True) and getattr(b, "skill", "") == "necromantic_denial" and getattr(b, "skill_active", False)]

        for user in skill_users:
            # Turn dead enemies into poison clouds
            to_remove = []
            for db in world.dead_balls:
                if getattr(db, "team", "") != user.team:
                    # Create cloud
                    cloud = VolatilePoisonCloud(db.x, db.y, user.team)
                    world.arena.hazards.append(cloud)
                    to_remove.append(db)

            for db in to_remove:
                world.dead_balls.remove(db)

            # Deactivate skill after use
            user.skill_active = False

        # Process existing clouds
        active_hazards = []
        for hazard in world.arena.hazards:
            if getattr(hazard, "kind", "") == "volatile_poison_cloud":
                # Expand
                if hazard.radius < hazard.max_radius:
                    hazard.radius = min(hazard.max_radius, hazard.radius + hazard.growth_rate * delta)

                # Damage enemies inside the cloud
                for b in balls:
                    if getattr(b, "alive", True) and getattr(b, "team", "") != hazard.team:
                        dist = math.hypot(b.x - hazard.x, b.y - hazard.y)
                        if dist <= hazard.radius:
                            dmg = hazard.damage_per_sec * delta
                            if hasattr(b, "take_damage"):
                                b.take_damage(dmg)
                            else:
                                b.hp -= dmg
                                if b.hp <= 0:
                                    b.alive = False

                hazard.timer -= delta
                if hazard.timer <= 0:
                    # Detonate!
                    for b in balls:
                        if getattr(b, "alive", True) and getattr(b, "team", "") != hazard.team:
                            dist = math.hypot(b.x - hazard.x, b.y - hazard.y)
                            if dist <= hazard.radius:
                                if hasattr(b, "take_damage"):
                                    b.take_damage(hazard.explosion_damage)
                                else:
                                    b.hp -= hazard.explosion_damage
                                    if b.hp <= 0:
                                        b.alive = False

                    if hasattr(world, "add_event"):
                        world.add_event("explosion", {"x": hazard.x, "y": hazard.y, "radius": hazard.radius, "damage": hazard.explosion_damage, "color": "green"})
                else:
                    active_hazards.append(hazard)
            else:
                active_hazards.append(hazard)

        world.arena.hazards = active_hazards
