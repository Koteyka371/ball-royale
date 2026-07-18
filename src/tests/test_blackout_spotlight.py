import pytest
from ai.game_modes import BlackoutMode
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

    def add_event(self, type_str, data):
        pass

class MockBall:
    def __init__(self, x=500, y=500, hp=100, team="red", ball_type="fighter"):
        self.x = x
        self.y = y
        self.hp = hp
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.radius = 15.0
        self.perception_radius = 250.0
        self.base_perception_radius = 250.0
        self.stamina = 50.0
        self.max_stamina = 100.0

def test_blackout_spotlight():
    mode = BlackoutMode()
    world = MockWorld()
    ball = MockBall()
    mode.setup(world, [ball])

    mode.is_blackout = True

    # Random seeding to guarantee spawn
    import random
    class MockRandom:
        def random(self): return 0.1
        def uniform(self, a, b): return 500.0
    mode.random = MockRandom()

    # Fast forward to spawn spotlight
    mode.tick(world, [ball], 3.5)

    # Check if spotlight spawned
    spotlights = [h for h in world.arena.hazards if getattr(h, "kind", "") == "spotlight"]
    assert len(spotlights) > 0

    # Place ball exactly at spotlight
    spotlight = spotlights[0]
    ball.x = spotlight.x
    ball.y = spotlight.y

    mode.tick(world, [ball], 0.1)

    # Check effects
    assert getattr(ball, "position_revealed", False) == True
    assert getattr(ball, "spotlight_damage_multiplier", 1.0) == 1.5
    assert ball.perception_radius > 50.0  # Kept high during blackout
