import math
import random
from ai.game_modes import GameMode

class MercenaryBall:
    def __init__(self, x, y, owner_team, owner_id):
        self.id = id(self)
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 20.0
        self.mass = 1.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "mercenary"
        self.team = owner_team
        self.owner_id = owner_id
        self.speed = 120.0
        self.base_speed = 120.0
        self.damage = 15.0
        self.base_damage = 15.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.perception_radius = 400.0
        self.base_perception_radius = 400.0

    def to_dict(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "radius": self.radius,
            "mass": self.mass,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "alive": self.alive,
            "ball_type": self.ball_type,
            "type": self.ball_type,
            "team": self.team,
            "owner_id": self.owner_id,
            "speed": getattr(self, "speed", 120.0),
            "base_speed": getattr(self, "base_speed", 120.0),
            "damage": getattr(self, "damage", 15.0),
            "base_damage": getattr(self, "base_damage", 15.0),
            "speed_multiplier": self.speed_multiplier,
            "damage_multiplier": self.damage_multiplier
        }

class MercenaryOutpostHazard:
    def __init__(self, x, y):
        self.kind = "mercenary_outpost"
        self.x = x
        self.y = y
        self.radius = 80.0
        self.capture_progress = 0.0
        self.capture_threshold = 10.0
        self.owner_id = None
        self.owner_team = None
        self.spawn_timer = 0.0
        self.spawn_interval = 5.0

class MercenaryOutpostsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Mercenary Outposts"
        self.description = "Capture outposts to spawn friendly mercenaries."
        self.active = False
        self.active_timer = 0.0

    def setup(self, world, balls):
        super().setup(world, balls)
        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []
        outposts = [h for h in world.arena.hazards if getattr(h, "kind", "") == "mercenary_outpost"]
        if not outposts:
            world.arena.hazards.append(MercenaryOutpostHazard(300.0, 300.0))
            world.arena.hazards.append(MercenaryOutpostHazard(700.0, 700.0))

    def apply_dynamic_traits(self, world, balls, delta):
        super().apply_dynamic_traits(world, balls, delta)

        for b in balls:
            if getattr(b, "ball_type", "") == "mercenary" and getattr(b, "alive", True):
                closest_enemy = None
                closest_dist = float('inf')
                for other in balls:
                    if getattr(other, "alive", True) and getattr(other, "team", None) != getattr(b, "team", None) and getattr(other, "ball_type", "") != "spectator":
                        dist = math.hypot(b.x - other.x, b.y - other.y)
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_enemy = other
                if closest_enemy and closest_dist < getattr(b, "perception_radius", 400.0):
                    dx = closest_enemy.x - b.x
                    dy = closest_enemy.y - b.y
                    mag = math.hypot(dx, dy)
                    if mag > 0:
                        b.vx = (dx / mag) * getattr(b, "speed", 120.0)
                        b.vy = (dy / mag) * getattr(b, "speed", 120.0)
                else:
                    owner = None
                    for other in balls:
                        if getattr(other, "id", None) == getattr(b, "owner_id", None):
                            owner = other
                            break
                    if owner:
                        dx = owner.x - b.x
                        dy = owner.y - b.y
                        mag = math.hypot(dx, dy)
                        if mag > 100:
                            b.vx = (dx / mag) * getattr(b, "speed", 120.0)
                            b.vy = (dy / mag) * getattr(b, "speed", 120.0)
                        else:
                            b.vx = 0.0
                            b.vy = 0.0
                b.x += b.vx * delta
                b.y += b.vy * delta

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)
        if not hasattr(world.arena, "hazards"):
            return

        if self.active:
            self.active_timer -= delta
            if self.active_timer <= 0.0:
                self.active = False

        new_mercenaries = []
        for h in world.arena.hazards:
            if getattr(h, "kind", "") == "mercenary_outpost":
                if h.capture_progress < h.capture_threshold:
                    capturing_balls = []
                    for b in balls:
                        if getattr(b, "alive", True) and getattr(b, "ball_type", "") != "spectator" and getattr(b, "ball_type", "") != "mercenary":
                            dist = math.hypot(b.x - h.x, b.y - h.y)
                            if dist < h.radius:
                                capturing_balls.append(b)

                    if len(capturing_balls) == 1:
                        cb = capturing_balls[0]
                        if h.owner_id != getattr(cb, "id", None):
                            h.owner_id = getattr(cb, "id", None)
                            h.owner_team = getattr(cb, "team", None)
                            h.capture_progress = 0.0
                        h.capture_progress += delta
                        if h.capture_progress >= h.capture_threshold:
                            h.capture_progress = h.capture_threshold
                            if hasattr(world, "events"):
                                world.events.append({
                                    'type': 'outpost_captured',
                                    'data': {
                                        'owner_id': h.owner_id
                                    }
                                })
                else:
                    h.spawn_timer += delta
                    if h.spawn_timer >= h.spawn_interval:
                        h.spawn_timer = 0.0
                        merc = MercenaryBall(h.x, h.y, h.owner_team, h.owner_id)
                        new_mercenaries.append(merc)

        if new_mercenaries:
            balls.extend(new_mercenaries)
