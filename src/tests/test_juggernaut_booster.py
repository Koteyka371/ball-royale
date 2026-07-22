import pytest
from unittest.mock import MagicMock

class MockBall:
    def __init__(self, id=1, team="A"):
        self.id = id
        self.team = team
        self.x = 100.0
        self.y = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.radius = 10.0
        self.mass = 1.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.speed = 100.0
        self.juggernaut_booster_timer = 0.0
        self.juggernaut_booster_applied = False
        self.intangible = False
        self.intangible_timer = 0.0

class MockHazard:
    def __init__(self, x=105.0, y=105.0, kind="juggernaut_booster"):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self, hazards=None):
        self.width = 1000
        self.height = 1000
        self.hazards = hazards if hazards else []

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters if boosters else []
        self.dead_balls = []

    def get_world_state(self, ball):
        return {
            "allies": [b for b in self.balls if getattr(b, "team", None) == ball.team],
            "enemies": [b for b in self.balls if getattr(b, "team", None) != ball.team],
            "boosters": self.boosters
        }

def test_juggernaut_booster_collection_and_tick():
    # Setup Action module structure
    import sys
    sys.path.insert(0, "src")
    from ai.action import Action

    ball = MockBall(1, "A")
    booster = MockHazard(105.0, 105.0, "juggernaut_booster")
    arena = MockArena(hazards=[booster])
    world = MockWorld(arena, [ball], boosters=[booster])
    action = Action(ball, world)

    # Bypass obstacle/flee logic for test
    action._get_enemies = lambda: []
    action._get_boosters = lambda: world.boosters

    # Act: Collection
    action._collect_booster(0.016)

    # Assert collection effect
    assert getattr(ball, "juggernaut_booster_timer", 0.0) == 15.0
    assert booster not in world.boosters
    assert booster not in arena.hazards

    # Act: Tick effect (should apply stats)
    action.execute("idle", 0.016)

    # Assert stat changes
    assert getattr(ball, "juggernaut_booster_applied", False) == True
    assert getattr(ball, "radius", 10.0) == 25.0
    assert getattr(ball, "mass", 1.0) == 5.0
    assert getattr(ball, "max_hp", 100.0) == 600.0
    assert getattr(ball, "hp", 100.0) == 600.0
    assert getattr(ball, "speed", 100.0) == 50.0

    # Act: Tick effect again (should not re-apply)
    action.execute("idle", 0.016)
    assert getattr(ball, "radius", 10.0) == 25.0

    # Fast-forward timer
    ball.juggernaut_booster_timer = 0.0
    action.execute("idle", 0.016)

    # Assert stats reverted
    assert getattr(ball, "juggernaut_booster_applied", False) == False
    assert getattr(ball, "radius", 25.0) == 10.0
    assert getattr(ball, "mass", 5.0) == 1.0
    assert getattr(ball, "max_hp", 600.0) == 100.0
    assert getattr(ball, "hp", 600.0) == 100.0
    assert getattr(ball, "speed", 50.0) == 100.0

if __name__ == "__main__":
    pytest.main(["-v", "test_juggernaut_booster.py"])
