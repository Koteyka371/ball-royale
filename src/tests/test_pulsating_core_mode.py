import pytest
import math
from ai.game_modes import PulsatingCoreMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.alive = True
        self.radius = 15.0

class MockHazard:
    def __init__(self, kind, team):
        self.kind = kind
        self.team = team
        self.x = 0.0
        self.y = 0.0
        self.pulse_timer = 0.016
        self.pulse_radius = 250.0

def test_pulsating_core_mode_push_pull():
    mode = PulsatingCoreMode()
    world = MockWorld()
    hazard = MockHazard("pulsating_core", "Team A")
    world.arena.hazards.append(hazard)

    ally = MockBall(50.0, 0.0, "Team A")
    enemy = MockBall(-50.0, 0.0, "Team B")

    balls = [ally, enemy]

    # Tick to decrement timer and apply force
    mode.apply_dynamic_traits(world, balls, 0.016)

    # Ally should be pulled towards (0,0), so vx should be negative
    assert ally.vx < -0.1

    # Enemy should be pushed away from (0,0), so vx should be negative as well (since they are at -50, dir_x is -1)
    assert enemy.vx < -0.1
