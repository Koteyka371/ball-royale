import pytest
from ai.game_modes import ExplosiveMeteorsMode
from unittest.mock import MagicMock

class MockBall:
    def __init__(self, name="TestBall"):
        self.name = name
        self.id = name
        self.x = 100.0
        self.y = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.slow_timer = 0.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.weather_immunity_timer = 0.0
        self.ball_type = "normal"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.traits = []
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 50.0
        self.invisible = False
        self.speed_multiplier = 1.0

def test_explosive_meteors_mode():
    mode = ExplosiveMeteorsMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.width = 1000
    world.arena.height = 1000
    world.arena.hazards = []

    world.leaderboard_manager = MagicMock()
    world.leaderboard_manager.data = {"current_season": 1}

    balls = [MockBall()]
    mode.setup(world, balls)

    # Tick loop to spawn meteors without clearing delay on the same tick
    for i in range(50):
        mode.tick(world, balls, delta=0.1)
    # The last tick makes it exactly 5.0
    mode.tick(world, balls, delta=0.1)

    assert len(mode.meteors) == 1
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "meteor_indicator"

    meteor = mode.meteors[0]
    # Move ball to first meteor
    balls[0].x = meteor["x"]
    balls[0].y = meteor["y"]

    # Fast forward to impact
    for i in range(30):
        mode.tick(world, balls, delta=0.1)

    # Should take 50 damage
    assert balls[0].hp == 50.0
    # Meteor should be removed
    assert len(mode.meteors) == 0
