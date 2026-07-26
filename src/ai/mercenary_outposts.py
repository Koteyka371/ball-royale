import math
from ai.game_modes import GameMode

class MercenaryOutpostsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Mercenary Outposts"
        self.description = "Players can capture mercenary outposts across the map. Once fully captured, friendly AI balls spawn periodically and help defend the capturing player."
        self.outposts = []
        self.mercenaries = []
        self.outpost_id_counter = 1000
        self.mercenary_id_counter = 5000

    def setup(self, world, balls):
        super().setup(world, balls)

        arena_w = getattr(world.arena, "width", 1000) if hasattr(world, "arena") else 1000
        arena_h = getattr(world.arena, "height", 1000) if hasattr(world, "arena") else 1000

        # Define outposts at 4 corners of the map
        self.outposts = [
            {"id": self.outpost_id_counter, "x": arena_w * 0.2, "y": arena_h * 0.2, "radius": 100.0, "owner": None, "capture_progress": 0.0, "spawn_timer": 0.0},
            {"id": self.outpost_id_counter + 1, "x": arena_w * 0.8, "y": arena_h * 0.8, "radius": 100.0, "owner": None, "capture_progress": 0.0, "spawn_timer": 0.0},
            {"id": self.outpost_id_counter + 2, "x": arena_w * 0.2, "y": arena_h * 0.8, "radius": 100.0, "owner": None, "capture_progress": 0.0, "spawn_timer": 0.0},
            {"id": self.outpost_id_counter + 3, "x": arena_w * 0.8, "y": arena_h * 0.2, "radius": 100.0, "owner": None, "capture_progress": 0.0, "spawn_timer": 0.0}
        ]
        self.outpost_id_counter += 4
        self.mercenaries = []

    def apply_dynamic_traits(self, world, balls, delta):
        # Update Outposts Capture Progress
        for outpost in self.outposts:
            occupying_teams = set()
            occupants = []

            for b in balls:
                if not getattr(b, "alive", False) or getattr(b, "ball_type", "") == "spectator":
                    continue
                # Ignore mercenaries for capturing logic
                if getattr(b, "is_mercenary", False):
                    continue

                dx = getattr(b, "x", 0.0) - outpost["x"]
                dy = getattr(b, "y", 0.0) - outpost["y"]
                dist = math.hypot(dx, dy)
                if dist <= outpost["radius"]:
                    team = getattr(b, "team", None)
                    if team:
                        occupying_teams.add(team)
                        occupants.append(b)

            if len(occupying_teams) == 1:
                team = list(occupying_teams)[0]
                if outpost["owner"] == team:
                    # Already owned, maybe heal or do something, for now just fully captured
                    outpost["capture_progress"] = 100.0
                elif outpost["owner"] is None:
                    # Capture neutral
                    outpost["capture_progress"] += 20.0 * delta
                    if outpost["capture_progress"] >= 100.0:
                        outpost["owner"] = team
                        outpost["capture_progress"] = 100.0
                        world.add_event("outpost_captured", {"team": team, "outpost": outpost})
                else:
                    # Contested by enemy, drain first
                    outpost["capture_progress"] -= 20.0 * delta
                    if outpost["capture_progress"] <= 0.0:
                        outpost["owner"] = None
                        outpost["capture_progress"] = 0.0
                        world.add_event("outpost_neutralized", {"outpost": outpost})
            elif len(occupying_teams) == 0:
                # Slowly decay to 0 if neutral, or heal to 100 if owned
                if outpost["owner"] is None:
                    outpost["capture_progress"] = max(0.0, outpost["capture_progress"] - 5.0 * delta)
                else:
                    outpost["capture_progress"] = min(100.0, outpost["capture_progress"] + 5.0 * delta)

            # Spawn Mercenaries if fully captured
            if outpost["owner"] and outpost["capture_progress"] >= 100.0:
                outpost["spawn_timer"] += delta
                if outpost["spawn_timer"] >= 10.0: # Spawn every 10 seconds
                    outpost["spawn_timer"] = 0.0
                    self.spawn_mercenary(world, balls, outpost)

    def spawn_mercenary(self, world, balls, outpost):
        # Create a dictionary entity which is common for generated mobs/boosters in python
        class Entity:
            pass
        merc = Entity()
        merc.id = self.mercenary_id_counter
        merc.x = outpost["x"]
        merc.y = outpost["y"]
        merc.vx = 0.0
        merc.vy = 0.0
        merc.radius = 20.0
        merc.hp = 100.0
        merc.max_hp = 100.0
        merc.alive = True
        merc.ball_type = "mercenary"
        merc.team = outpost["owner"]
        merc.speed = 150.0
        merc.base_speed = 150.0
        merc.damage = 10.0
        merc.base_damage = 10.0
        merc.is_mercenary = True
        merc.speed_multiplier = 1.0
        merc.damage_multiplier = 1.0
        merc.mass = 1.0

        def to_dict():
            return {
                "id": merc.id,
                "x": merc.x,
                "y": merc.y,
                "radius": merc.radius,
                "hp": merc.hp,
                "max_hp": merc.max_hp,
                "team": merc.team,
                "type": "mercenary",
                "alive": merc.alive,
            }
        merc.to_dict = to_dict

        self.mercenary_id_counter += 1

        balls.append(merc)
        if hasattr(world, "entities"):
            world.entities.append(merc)
        if hasattr(world, "balls") and merc not in world.balls:
            world.balls.append(merc)

        world.add_event("mercenary_spawned", {"team": outpost["owner"], "x": outpost["x"], "y": outpost["y"]})
