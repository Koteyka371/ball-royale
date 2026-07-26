import math
from ai.game_modes import GameMode

class CaptureTheFlagElementsInBattleRoyaleMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Capture The Flag Elements in Battle Royale"
        self.description = "Spawn flags in neutral capture zones. If a player captures the flag and brings it to the center zone, they gain massive stat boosts for the duration of the match."
        self.center_zone = {"x": 500.0, "y": 500.0, "radius": 150.0}
        self.neutral_zones = []

    def setup(self, world, balls):
        super().setup(world, balls)

        arena_w = getattr(world.arena, "width", 1000) if hasattr(world, "arena") else 1000
        arena_h = getattr(world.arena, "height", 1000) if hasattr(world, "arena") else 1000

        self.center_zone = {"x": arena_w / 2, "y": arena_h / 2, "radius": 100.0}

        self.neutral_zones = [
            {"x": arena_w * 0.1, "y": arena_h * 0.1, "radius": 50.0},
            {"x": arena_w * 0.9, "y": arena_h * 0.9, "radius": 50.0},
            {"x": arena_w * 0.1, "y": arena_h * 0.9, "radius": 50.0},
            {"x": arena_w * 0.9, "y": arena_h * 0.1, "radius": 50.0}
        ]

        if not hasattr(world, "boosters"):
            world.boosters = []

        class FlagBooster:
            def __init__(self, id, x, y, team):
                self.id = id
                self.x = x
                self.y = y
                self.is_flag = True
                self.team = team
                self.carrier = None
                self.ball_type = "booster"

        for i, zone in enumerate(self.neutral_zones):
            flag = FlagBooster(f"neutral_flag_{i}", zone["x"], zone["y"], "Neutral")
            world.boosters.append(flag)

        self.boosted_players = set()

    def tick(self, world, delta: float) -> None:
        if not hasattr(world, "balls"):
            return

        cx, cy, cr = self.center_zone["x"], self.center_zone["y"], self.center_zone["radius"]

        for b in world.balls:
            if not getattr(b, "alive", False):
                continue

            if getattr(b, "id", None) in self.boosted_players:
                continue

            bx = getattr(b, "x", 0.0)
            by = getattr(b, "y", 0.0)

            dist = math.hypot(bx - cx, by - cy)

            if getattr(b, "has_flag", False) and dist <= cr:
                b.has_flag = False

                # Apply massive stat boost
                if hasattr(b, "base_speed"):
                    b.base_speed *= 2.0
                    b.speed = getattr(b, "speed", b.base_speed) * 2.0
                else:
                    b.speed = getattr(b, "speed", 100.0) * 2.0
                    b.base_speed = b.speed

                if hasattr(b, "base_damage"):
                    b.base_damage *= 3.0
                    b.damage = getattr(b, "damage", b.base_damage) * 3.0
                else:
                    b.damage = getattr(b, "damage", 10.0) * 3.0
                    b.base_damage = b.damage

                if hasattr(b, "max_hp"):
                    b.max_hp += 500.0
                    b.hp = getattr(b, "hp", 100.0) + 500.0
                else:
                    b.hp = getattr(b, "hp", 100.0) + 500.0
                    b.max_hp = b.hp

                self.boosted_players.add(getattr(b, "id", None))

                if hasattr(world, "add_event"):
                    world.add_event("flag_captured_center", {"player_id": getattr(b, "id", None), "message": "Massive stats boost acquired!"})
