import pytest
from ai.game_modes import GameMode, CorruptionZonesEventMode

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockArena:
    def __init__(self):
        self.width = 2000.0
        self.height = 2000.0
        self.hazards = []

class MockBall:
    def __init__(self, x, y):
        self.id = 1
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.ball_type = "normal"
        self.damage_multiplier = 1.0
        self.speed_multiplier = 1.0

def test_corruption_zone_mechanics():
    mode = CorruptionZonesEventMode()
    world = MockWorld()

    ball_inside = MockBall(100.0, 100.0)
    ball_outside = MockBall(1000.0, 1000.0)
    balls = [ball_inside, ball_outside]

    # Fast forward to trigger spawn
    mode.zone_spawn_timer = 0.01
    mode.tick(world, balls, delta=0.016)

    assert len(world.arena.hazards) == 1
    zone = world.arena.hazards[0]
    assert zone.kind == "corruption_zone"

    # Move zone to ball_inside
    zone.x = 100.0
    zone.y = 100.0

    # Tick again to apply effects
    mode.tick(world, balls, delta=1.0)

    # Inside ball should be damaged and buffed
    assert ball_inside.hp < 100.0
    assert ball_inside.damage_multiplier == 2.5
    assert ball_inside.speed_multiplier == 1.8

    # Outside ball should be unaffected
    assert ball_outside.hp == 100.0
    assert ball_outside.damage_multiplier == 1.0
    assert ball_outside.speed_multiplier == 1.0
