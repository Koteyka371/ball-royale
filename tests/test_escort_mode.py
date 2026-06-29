import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ai.game_modes import EscortMode

class MockBall:
    def __init__(self, id, ball_type="basic"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.x = 0.0
        self.y = 0.0
        self.team = "None"
        self.speed = 100
        self.base_speed = 100

class MockWorld:
    def __init__(self):
        self.dead_balls = []

def test_escort_mode_setup():
    mode = EscortMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]

    mode.setup(world, balls)

    # Defenders should have 1 payload and 1 regular defender
    payload = None
    defenders = []
    attackers = []

    for b in balls:
        if b.team == "Payload":
            payload = b
        elif b.team == "Defenders":
            defenders.append(b)
        elif b.team == "Attackers":
            attackers.append(b)

    assert payload is not None
    assert payload.max_hp == 1000
    assert payload.hp == 1000
    assert payload.base_speed == 20.0
    assert payload.x == 100.0
    assert payload.y == 500.0
    assert len(defenders) == 1
    assert len(attackers) == 2

def test_escort_mode_tick_movement():
    mode = EscortMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]

    mode.setup(world, balls)
    payload = mode.payload

    assert payload.x == 100.0
    mode.tick(world, balls, delta=1.0) # Move payload
    assert payload.x > 100.0 # Moving towards 900

def test_escort_mode_win_conditions():
    mode = EscortMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]

    mode.setup(world, balls)

    # Init winner state should be None
    assert mode.check_winner(world, balls) is None

    # If payload dies, attackers win
    mode.payload.alive = False
    assert mode.check_winner(world, balls) == "Attackers"

    # Reset payload
    mode.payload.alive = True

    # If payload reaches goal, defenders win
    mode.payload.x = mode.goal_x
    mode.payload.y = mode.goal_y
    assert mode.check_winner(world, balls) == "Defenders"

    # Reset payload position
    mode.payload.x = 100.0
    mode.payload.y = 500.0

    # If attackers die, defenders win
    for b in balls:
        if b.team == "Attackers":
            b.alive = False

    assert mode.check_winner(world, balls) == "Defenders"
