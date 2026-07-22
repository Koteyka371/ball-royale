import pytest
from src.ai.game_modes import ShrinkingDangerZoneMode

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "basic"
        self.team = "basic"

class MockWorld:
    def __init__(self):
        self.events = []
        self.dead_balls = []

    def add_event(self, name, data):
        self.events.append(data)

def test_collapse_event():
    world = MockWorld()
    ball1 = MockBall(x=500.0, y=400.0)
    ball2 = MockBall(x=500.0, y=600.0)
    balls = [ball1, ball2]

    mode = ShrinkingDangerZoneMode()
    mode.setup(world, balls)

    # Ensure zone is small enough to trigger collapse on next tick
    mode.zone_radius = mode.min_zone_radius + 0.1
    mode.shrink_rate = 1.0 # 1 * 0.1 = 0.1
    mode.tick(world, balls, delta=0.1)

    # It should hit exactly min_zone_radius and trigger collapse
    assert mode.collapse_triggered == True
    collapse_events = [e for e in world.events if e.get("type") == "collapse_event"]
    assert len(collapse_events) == 1

    # Check that it pulls balls to center (500, 500)
    mode.tick(world, balls, delta=0.1)

    # Ball 1 is at y=400, center is 500. So dy = 100. dy/dist = 1.0.
    # vx += 0, vy += 1 * 2000 * 0.1 = 200
    assert ball1.vy > 0
    assert ball2.vy < 0

    # Verify zone shrinks past min
    assert mode.zone_radius < mode.min_zone_radius

    # Verify extra damage applied
    # Normal damage is outside_damage_per_second * delta (20.0 * 0.1 = 2)
    # Collapse damage is * 10 (20.0 * 10 * 0.1 = 20)

    # Move ball outside
    ball1.y = 0.0
    mode.tick(world, [ball1], delta=0.1)
    # hp should be reduced by 20
    assert ball1.hp <= 80.0
