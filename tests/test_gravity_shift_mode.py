import pytest
from ai.game_modes import GravityShiftMode

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y, prestige=0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.active = True
        self.prestige = prestige
        self.action_deploy_anchor = False
        self.anchor_cooldown = 0.0

def test_gravity_shift_mode():
    mode = GravityShiftMode()
    world = MockWorld()
    ball1 = MockBall("b1", 100.0, 100.0, prestige=5)
    ball2 = MockBall("b2", -50.0, -50.0, prestige=1)
    balls = [ball1, ball2]

    mode.setup(world, balls)
    mode.shift_timer = 0.1 # Trigger shift soon

    # Tick to trigger shift
    mode.tick(world, balls, 0.15)

    assert mode.shift_duration > 0
    assert mode.shift_type in ["point", "edges"]
    assert len(world.events) > 0
    assert world.events[0][0] == "gravity_shift"

    # Deploy anchor for ball 1
    ball1.action_deploy_anchor = True
    mode.tick(world, balls, 0.1)

    assert len(mode.anchors) == 1
    assert mode.anchors[0]['owner_id'] == "b1"
    assert ball1.anchor_cooldown > 0

    # Tick with gravity active
    initial_vx_b1 = ball1.vx
    initial_vy_b1 = ball1.vy
    initial_vx_b2 = ball2.vx
    initial_vy_b2 = ball2.vy

    mode.tick(world, balls, 0.1)

    # Ball 1 is anchored, should not have changed velocity
    assert ball1.vx == initial_vx_b1
    assert ball1.vy == initial_vy_b1

    # Ball 2 is not anchored, should have changed velocity
    assert ball2.vx != initial_vx_b2 or ball2.vy != initial_vy_b2
