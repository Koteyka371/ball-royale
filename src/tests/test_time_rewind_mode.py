import sys; sys.path.append('src')
import pytest
from ai.game_modes import TimeRewindMode

class MockBall:
    def __init__(self, bid):
        self.id = bid
        self.alive = True
        self.ball_type = "player"
        self.x = 0.0
        self.y = 0.0
        self.hp = 100.0

class MockWorld:
    def __init__(self):
        self.events = []
        self.mutators_active = False
        self.dead_balls = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_time_rewind_mode():
    mode = TimeRewindMode()
    world = MockWorld()
    b = MockBall("b1")
    balls = [b]

    # Tick for 25 seconds
    for _ in range(250):
        b.x += 1.0
        b.hp -= 0.1
        mode.tick(world, balls, 0.1)

    # Note state at 25 seconds
    state_at_25_x = b.x
    state_at_25_hp = b.hp
    print("State at 25s: x =", state_at_25_x, ", hp =", state_at_25_hp)

    # Tick for 5 more seconds to hit 30
    for _ in range(49):
        b.x += 1.0
        b.hp -= 0.1
        mode.tick(world, balls, 0.1)

    print("State at 29.9s: x =", b.x, ", hp =", b.hp)

    # The 300th tick should trigger rewind
    b.x += 1.0
    b.hp -= 0.1
    mode.tick(world, balls, 0.1)

    print("State at 30s: x =", b.x, ", hp =", b.hp)

    # After hitting 30, it should have rewound back to the state at 25 seconds
    assert b.x == pytest.approx(state_at_25_x, abs=1.5)
    assert b.hp == pytest.approx(state_at_25_hp, abs=1.5)
