import pytest
from unittest.mock import MagicMock
from ai.game_modes import ChainTetherMode

class MockBall:
    def __init__(self, id_val, x=0.0, y=0.0):
        self.id = id_val
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0
        self.stun_timer = 0.0

def test_chain_tether_initial_link():
    mode = ChainTetherMode()
    world = MagicMock()

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 100, 0)
    b3 = MockBall(3, 300, 0)

    balls = [b1, b2, b3]

    mode.tick(world, balls, 0.1)

    assert b1.chain_target_id == 2  # b2 is closest to b1
    assert b2.chain_target_id == 1  # b1 is closest to b2
    assert b3.chain_target_id == 2  # b2 is closest to b3

def test_chain_tether_damage_and_visual():
    mode = ChainTetherMode()
    world = MagicMock()
    world.events = []
    def add_event(type, data):
        data['type'] = type
        world.events.append(data)
    world.add_event = add_event

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 50, 0)
    balls = [b1, b2]

    mode.tick(world, balls, 0.1)

    # Check link established
    assert b1.chain_target_id == 2
    assert getattr(b1, "chain_link_time", 0.0) > 0.0

    # Tick again to apply damage
    mode.tick(world, balls, 0.1)

    assert getattr(b1, "chain_link_time", 0.0) > 0.1
    assert b1.hp < 100.0

    # Check visual event
    events = [e for e in world.events if e['type'] == 'visual_effect']
    assert len(events) > 0

def test_chain_tether_snap():
    mode = ChainTetherMode()
    world = MagicMock()
    world.events = []
    def add_event(type, data):
        data['type'] = type
        world.events.append(data)
    world.add_event = add_event

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 100, 0)
    balls = [b1, b2]

    mode.tick(world, balls, 0.1)

    # Link established
    assert b1.chain_target_id == 2

    # Move too far
    b2.x = 1000.0

    mode.tick(world, balls, 0.1)

    # Link snapped
    assert b1.chain_target_id is None
    assert b1.stun_timer > 0.0
    assert b2.stun_timer > 0.0

    snap_events = [e for e in world.events if e['type'] == 'chain_snap']
    assert len(snap_events) > 0
