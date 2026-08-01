import pytest
from ai.game_modes import FactionWarMode

class MockWorld:
    def __init__(self):
        self.damaged_entities = []
        self.dead_balls = []
        self.arena = type("MockArena", (), {"hazards": []})()
        self.match_time = 0.0

    def _deal_damage(self, attacker, target, amount):
        self.damaged_entities.append((target, amount))
        if isinstance(target, dict):
            target["hp"] -= amount
            if target["hp"] <= 0:
                target["active"] = False
                target["alive"] = False
        else:
            target.hp -= amount
            if target.hp <= 0:
                target.active = False
                target.alive = False

def test_faction_superweapon():
    mode = FactionWarMode()
    world = MockWorld()

    class MockBall:
        def __init__(self, i, faction):
            self.id = i
            self.x = 100.0
            self.y = 100.0
            self.ball_type = "bot"
            self.faction = faction
            self.active = True
            self.alive = True
            self.hp = 100
            self.radius = 15.0
            self.speed = 100
            self.base_speed = 100

    # 4 light balls, 4 dark balls
    balls = [MockBall(i, "Light") for i in range(4)] + [MockBall(i+4, "Dark") for i in range(4)]

    mode.light_points = 5
    mode.dark_points = 0
    mode.tick(world, balls)

    # Light is winning by 5, so Dark gets the superweapon
    assert mode.superweapon_spawned
    assert mode.superweapon_faction == "Dark"
    assert mode.superweapon_pos == (0.0, 0.0)

    # Move a dark ball to the superweapon
    balls[4].x = 0.0
    balls[4].y = 0.0
    mode.tick(world, balls)

    # Superweapon should be collected
    assert mode.superweapon_pos is None

    # Check if half of light balls (2) were eliminated
    active_light = sum(1 for b in balls[:4] if b.active)
    assert active_light == 2
