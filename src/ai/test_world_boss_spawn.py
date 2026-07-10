import pytest
from unittest.mock import Mock
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

class MockBall:
    def __init__(self):
        self.id = "original"
        self.alive = True
        self.ball_type = "paladin"
        self.level = 9
        self.experience = 900
        self.max_hp = 100.0
        self.hp = 100.0
        self.damage = 10.0
        self.speed = 100.0
        self.radius = 15.0
        self.x = 0.0
        self.y = 0.0

def test_world_boss_spawn():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)

    action = Action(ball, world)

    # We will mock random.random to return 0.1 so it spawns
    import random
    original_random = random.random
    try:
        random.random = lambda: 0.1

        # Level up to 10. Needs 100 xp
        action._award_xp(ball, 100, world)

        # Check if corrupted clone spawned
        assert len(world.balls) == 2
        corrupted = world.balls[-1]

        assert corrupted.team == "world_boss"
        assert corrupted.is_boss == True
        assert corrupted.ball_type == "warrior" # Paladin base is warrior
        assert corrupted.max_hp == 500.0
        assert corrupted.hp == 500.0
        assert corrupted.damage == 20.0
        assert corrupted.speed == 120.0
        assert corrupted.radius == 30.0
        assert corrupted.cosmetic == "corrupted_aura"

        events = [e[0] for e in world.events]
        assert "world_boss_spawned" in events
    finally:
        random.random = original_random
