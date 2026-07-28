import pytest
from typing import Any, List

# Setup path so modules can be imported
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from ai.game_modes import GameMode, ChaoticStatHazardMode

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.id = id(self)
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.ball_type = "normal"

        self.speed = 100.0
        self.damage = 10.0
        self.mass = 2.0
        self.hp = 100.0
        self.max_hp = 100.0

def test_chaotic_stat_hazard_setup():
    mode = ChaoticStatHazardMode()
    world = MockWorld()
    mode.setup(world, [])
    assert len(world.arena.hazards) == 3
    for h in world.arena.hazards:
        assert h["kind"] == "random_stat_hazard"

def test_chaotic_stat_hazard_apply():
    mode = GameMode() # using base game mode to apply dynamic traits
    world = MockWorld()

    # Place a ball exactly on the hazard
    ball = MockBall(400, 300)

    hazard = {
        "kind": "random_stat_hazard",
        "x": 400.0,
        "y": 300.0,
        "radius": 80.0,
        "tick_interval": 1.0,
        "stat_tick_timer": 0.0
    }

    world.arena.hazards.append(hazard)

    # Store old stats
    old_speed = ball.speed
    old_damage = ball.damage
    old_mass = ball.mass
    old_hp = ball.hp

    import random
    random.seed(42) # set seed to have predictable results

    # Tick should trigger stat change
    mode.apply_dynamic_traits(world, [ball], 0.1)

    # We should have an event and stat change
    # Note: random.choice will pick one stat
    changed = False
    if ball.speed != old_speed: changed = True
    if ball.damage != old_damage: changed = True
    if ball.mass != old_mass: changed = True
    if ball.hp != old_hp: changed = True

    assert changed, "At least one stat should have been changed"
    assert len(world.events) > 0
    assert world.events[0][0] == "random_stat_hazard_proc"
