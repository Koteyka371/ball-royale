from typing import Any, List, Dict
import math

class MercenaryOutpostsMode:
    def __init__(self):
        self.id = "Mercenary Outposts"
        self.name = "Mercenary Outposts"
        self.description = "Players can capture mercenary outposts across the map. Once fully captured, friendly AI balls spawn periodically and help defend the capturing player."
        self.outposts = []
        self.random = __import__("random").Random(12345)

    def setup(self, world: Any, balls: List[Any]) -> None:
        self.outposts = []
        if hasattr(world, "tick_timer"):
            self.random = __import__("random").Random(int(world.tick_timer * 1000))

        arena_width = getattr(getattr(world, "arena", None), "width", 1000)
        arena_height = getattr(getattr(world, "arena", None), "height", 1000)

        # Create outposts
        num_outposts = 3
        for i in range(num_outposts):
            x = self.random.uniform(200, arena_width - 200)
            y = self.random.uniform(200, arena_height - 200)
            outpost = {
                "id": f"outpost_{self.random.randint(1000, 9999)}",
                "x": x,
                "y": y,
                "radius": 80.0,
                "kind": "mercenary_outpost",
                "capturing_team": None,
                "capture_progress": 0.0,
                "controlling_team": None,
                "spawn_timer": 0.0,
                "spawn_interval": 10.0,
                "active": True
            }
            self.outposts.append(outpost)

            if hasattr(world, "arena"):
                if not hasattr(world.arena, "hazards"):
                    world.arena.hazards = []

                try:
                    from arena.procedural_arena import Hazard
                    h = Hazard(id=outpost["id"], x=x, y=y, radius=80.0, kind="mercenary_outpost", damage=0.0)
                except ImportError:
                    class DummyHazard:
                        def __init__(self, id, x, y, radius, kind, damage):
                            self.id = id
                            self.x = x
                            self.y = y
                            self.radius = radius
                            self.kind = kind
                            self.damage = damage
                            self.active = True
                    h = DummyHazard(outpost["id"], x, y, 80.0, "mercenary_outpost", 0.0)

                setattr(h, "capture_progress", 0.0)
                setattr(h, "controlling_team", None)
                world.arena.hazards.append(h)

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        for outpost in self.outposts:
            if not outpost["active"]: continue

            balls_inside = []
            for b in balls:
                is_alive = b.get("alive", False) if isinstance(b, dict) else getattr(b, "alive", False)
                if not is_alive: continue

                ball_type = b.get("ball_type", "") if isinstance(b, dict) else getattr(b, "ball_type", "")
                if ball_type in ["spectator", "mercenary"]: continue

                bx = b.get("x", 0.0) if isinstance(b, dict) else getattr(b, "x", 0.0)
                by = b.get("y", 0.0) if isinstance(b, dict) else getattr(b, "y", 0.0)

                if math.hypot(bx - outpost["x"], by - outpost["y"]) < outpost["radius"]:
                    balls_inside.append(b)

            if balls_inside:
                teams_inside = []
                for b in balls_inside:
                    if isinstance(b, dict):
                        t = b.get("team", b.get("ball_type", ""))
                    else:
                        t = getattr(b, "team", getattr(b, "ball_type", ""))
                    teams_inside.append(t)
                teams_inside = list(set(teams_inside))

                if len(teams_inside) == 1:
                    team = teams_inside[0]
                    if outpost["capturing_team"] == team or outpost["capturing_team"] is None:
                        outpost["capturing_team"] = team
                        if outpost["controlling_team"] != team:
                            outpost["capture_progress"] += 15.0 * delta
                            if outpost["capture_progress"] >= 100.0:
                                outpost["controlling_team"] = team
                                outpost["capture_progress"] = 100.0
                                outpost["spawn_timer"] = outpost["spawn_interval"]
                                if hasattr(world, "add_event"):
                                    world.add_event("outpost_captured", {"team": team, "outpost_id": outpost["id"]})
                    else:
                        outpost["capture_progress"] -= 15.0 * delta
                        if outpost["capture_progress"] <= 0.0:
                            remainder = -outpost["capture_progress"]
                            outpost["capturing_team"] = team
                            outpost["controlling_team"] = None
                            outpost["capture_progress"] = remainder
                            if outpost["capture_progress"] >= 100.0:
                                outpost["controlling_team"] = team
                                outpost["capture_progress"] = 100.0
                else:
                    pass
            else:
                if outpost["controlling_team"] != outpost["capturing_team"] and outpost["capturing_team"] is not None:
                    outpost["capture_progress"] = max(0.0, outpost["capture_progress"] - 5.0 * delta)
                    if outpost["capture_progress"] == 0:
                        outpost["capturing_team"] = None

            if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                for h in world.arena.hazards:
                    if getattr(h, "id", "") == outpost["id"]:
                        setattr(h, "capture_progress", outpost["capture_progress"])
                        setattr(h, "controlling_team", outpost["controlling_team"])

            if outpost["controlling_team"] is not None:
                outpost["spawn_timer"] += delta
                if outpost["spawn_timer"] >= outpost["spawn_interval"]:
                    outpost["spawn_timer"] = 0.0
                    self.spawn_mercenary(world, balls, outpost)

    def spawn_mercenary(self, world: Any, balls: List[Any], outpost: Dict) -> None:
        team = outpost["controlling_team"]

        class MercenaryBall:
            def __init__(self, id, x, y, team):
                self.id = id
                self.x = x
                self.y = y
                self.vx = 0.0
                self.vy = 0.0
                self.radius = 20.0
                self.mass = 1.0
                self.hp = 50.0
                self.max_hp = 50.0
                self.team = team
                self.ball_type = "mercenary"
                self.alive = True
                self.speed_multiplier = 1.0
                self.damage_multiplier = 1.0
                self.speed = 200.0
                self.base_speed = 200.0
                self.shield = 0.0
                self.damage = 10.0
                self.ai_target = None
                self.is_intangible = False

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
                    "team": self.team,
                    "ball_type": self.ball_type,
                    "alive": self.alive,
                    "speed_multiplier": self.speed_multiplier,
                    "damage_multiplier": self.damage_multiplier,
                    "speed": self.speed,
                    "base_speed": self.base_speed
                }

        merc = MercenaryBall(
            id=f"merc_{self.random.randint(1000, 9999)}_{outpost['id']}",
            x=outpost["x"],
            y=outpost["y"],
            team=team
        )

        balls.append(merc)
        if hasattr(world, "entities"):
            world.entities.append(merc)
        if hasattr(world, "balls"):
            if merc not in world.balls:
                world.balls.append(merc)

    def check_winner(self, world, balls):
        return None # Rely on default logic
