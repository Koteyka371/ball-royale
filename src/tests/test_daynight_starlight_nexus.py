import pytest
from ai.game_modes import DayNightMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.is_night = True
        self.hazards = []
        self.items = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, t, d):
        self.events.append({"type": t, "data": d})

class MockBall:
    def __init__(self, id, team, traits, ball_type):
        self.id = id
        self.team = team
        self.traits = traits
        self.ball_type = ball_type
        self.alive = True
        self.x = 500
        self.y = 500

def test_starlight_nexus_spawn_and_destroy():
    mode = DayNightMode()
    world = MockWorld()
    balls = [MockBall(1, "A", ["shadow", "fast"], "shadow_assassin"), MockBall(2, "B", ["fire"], "fireball")]

    # Fast forward to mid-night and force spawn
    mode.timer = 6.0
    import random
    original_random = random.random
    random.random = lambda: 0.01  # Guarantee spawn
    try:
        mode.tick(world, balls, 0.1)
    finally:
        random.random = original_random

    assert mode.starlight_nexus_spawned == True
    assert len(world.arena.hazards) == 1
    nexus = world.arena.hazards[0]
    assert nexus.kind == "starlight_nexus"

    # Damage the nexus
    nexus.hp -= 1000.0 # destroy it
    # Move ball 1 slightly to be nearest
    balls[0].x = 500
    balls[0].y = 500
    balls[1].x = 100
    balls[1].y = 100

    mode.tick(world, balls, 0.1)

    # It should be destroyed and team A granted celestial aura
    assert len(world.arena.hazards) == 0
    assert hasattr(world, "celestial_aura_team")
    assert world.celestial_aura_team == "A"

    # Ball 1 traits should be updated
    assert "radiant" in balls[0].traits
    assert "celestial_aura" in balls[0].traits
    assert "shadow" not in balls[0].traits
    assert "radiant_assassin" in balls[0].ball_type

    # Ball 2 should be unaffected
    assert "fire" in balls[1].traits
