import pytest
import math
from ai.frictionless_modifier_mode import FrictionlessArenaModifierMode

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, alive=True):
        self.alive = alive
        self.is_frictionless = False

def test_frictionless_modifier_toggles():
    mode = FrictionlessArenaModifierMode()
    world = MockWorld()
    b1 = MockBall()
    b2 = MockBall(alive=False)
    balls = [b1, b2]

    mode.setup(world, balls)

    # Should start inactive with a timer between 10 and 30
    assert mode.frictionless_active == False
    assert 10.0 <= mode.timer <= 30.0

    # Fast forward just before timer expires
    mode.tick(world, balls, delta=mode.timer - 0.01)
    assert mode.frictionless_active == False

    # Trigger the switch to active
    mode.tick(world, balls, delta=0.02)
    assert mode.frictionless_active == True
    assert b1.is_frictionless == True
    assert getattr(b2, "is_frictionless", False) == False # b2 is dead, should not be set

    # Verify event sent
    events = [e for e in world.events if e[0] == "frictionless_modifier"]
    assert len(events) == 1
    assert "completely frictionless" in events[-1][1]["message"]

    # Reset is_frictionless to test next tick logic
    b1.is_frictionless = False

    # Fast forward to next switch
    timer_val = mode.timer
    assert 5.0 <= timer_val <= 15.0

    # Another tick while active shouldn't send duplicate event, but should set is_frictionless
    mode.tick(world, balls, delta=0.5)
    assert b1.is_frictionless == True
    assert len([e for e in world.events if e[0] == "frictionless_modifier"]) == 1 # Still 1

    # Trigger switch to inactive
    mode.tick(world, balls, delta=timer_val)
    assert mode.frictionless_active == False

    # Verify new event
    events = [e for e in world.events if e[0] == "frictionless_modifier"]
    assert len(events) == 2
    assert "Friction has returned to normal" in events[-1][1]["message"]

    # Verify is_frictionless is False
    assert b1.is_frictionless == False
