import pytest
from ai.game_modes import AuraIntensifierFieldMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.dead_balls = []
        self.time = 0.0

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.radius = 10.0
        self.aura_intensity = 0.0
        self.cosmetic_aura_scale = 1.0

def test_aura_intensifier_field():
    mode = AuraIntensifierFieldMode()
    world = MockWorld()

    # Create two balls, one inside, one outside
    b1 = MockBall(1, 500.0, 500.0) # inside
    b2 = MockBall(2, 100.0, 100.0) # outside
    world.balls.extend([b1, b2])

    mode.setup(world, world.balls)

    assert len(mode.zones) > 0

    # Force one zone to a specific location for testing
    zone = mode.zones[0]
    zone.x = 500.0
    zone.y = 500.0
    zone.radius = 100.0
    zone.active = True

    mode.tick(world, world.balls, 1.0)

    # b1 should have lost HP and gained aura
    assert b1.hp == 95.0
    assert b1.aura_intensity == 1.0
    assert b1.cosmetic_aura_scale == 1.1

    # b2 should be unaffected
    assert b2.hp == 100.0
    assert b2.aura_intensity == 0.0
    assert b2.cosmetic_aura_scale == 1.0

    # Test killing a ball
    b1.hp = 2.0
    mode.tick(world, world.balls, 1.0)

    assert b1.hp == 0.0
    assert not b1.alive
    assert any(e[0] == "ball_died" and e[1]["id"] == 1 for e in world.events)

if __name__ == "__main__":
    pytest.main(["-s", __file__])
