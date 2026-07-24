import pytest
from ai.game_modes import ChainLightningEventMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.damage_events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

    def _deal_damage(self, source, target, amount):
        self.damage_events.append((source, target, amount))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.chain_lightning_conduit_timer = 0.0
        self.chain_lightning_arc_timer = 0.0

def test_chain_lightning_strike():
    mode = ChainLightningEventMode()
    world = MockWorld()

    b1 = MockBall("b1", 500, 500) # Center
    b2 = MockBall("b2", 100, 100) # Far away
    balls = [b1, b2]

    mode.strike_timer = 19.9
    mode.tick(world, balls, delta=0.2)

    assert mode.strike_timer == 0.0

    # Check events
    strike_events = [e for e in world.events if e[0] == "chain_lightning_strike"]
    assert len(strike_events) == 1
    assert strike_events[0][1]["x"] == 500.0
    assert strike_events[0][1]["y"] == 500.0
    assert strike_events[0][1]["radius"] == 200.0

    # Check conduit application
    assert getattr(b1, "chain_lightning_conduit_timer", 0.0) == 9.8
    assert getattr(b2, "chain_lightning_conduit_timer", 0.0) == 0.0

def test_chain_lightning_arcs():
    mode = ChainLightningEventMode()
    world = MockWorld()

    b1 = MockBall("b1", 500, 500)
    b1.chain_lightning_conduit_timer = 5.0
    b1.chain_lightning_arc_timer = 0.0

    b2 = MockBall("b2", 550, 500) # Close to b1
    b3 = MockBall("b3", 900, 900) # Far from b1
    balls = [b1, b2, b3]

    mode.tick(world, balls, delta=0.1)

    # Check conduit timer reduced
    assert getattr(b1, "chain_lightning_conduit_timer", 0.0) < 5.0

    # Check damage was dealt to b2 but not b3
    assert len(world.damage_events) == 1
    assert world.damage_events[0][0] == b1
    assert world.damage_events[0][1] == b2
    assert world.damage_events[0][2] == 5.0

    # Check arc visual events
    arc_events = [e for e in world.events if e[0] == "chain_lightning_arc"]
    assert len(arc_events) == 1
    assert arc_events[0][1]["source"] == "b1"
    assert arc_events[0][1]["target"] == "b2"
