import pytest
from unittest.mock import MagicMock
from src.ai.game_modes import VampiricZoneMode

class MockWorld:
    def __init__(self):
        self.arena = MagicMock()
        self.arena.width = 1000
        self.arena.height = 1000
        self.arena.hazards = []
        self.events = []
        self.dead_balls = []

class MockBall:
    def __init__(self, id, team, x, y, hp=100):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100
        self.ball_type = "player"
        self.alive = True

def test_vampiric_zone_setup():
    mode = VampiricZoneMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    assert mode.zone_x == 500
    assert mode.zone_y == 500
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "vampiric_zone"
    assert world.arena.hazards[0].x == 500
    assert world.arena.hazards[0].y == 500

def test_vampiric_zone_damage_and_heal():
    mode = VampiricZoneMode()
    world = MockWorld()

    # Target in center (zone is at 500, 500)
    target = MockBall(1, team=1, x=500, y=500, hp=100)
    # Enemy out of zone, but closer than the other enemy
    enemy1 = MockBall(2, team=2, x=700, y=700, hp=50)
    # Enemy further away
    enemy2 = MockBall(3, team=2, x=900, y=900, hp=50)
    # Teammate close (should not be healed)
    teammate = MockBall(4, team=1, x=600, y=600, hp=50)

    balls = [target, enemy1, enemy2, teammate]
    mode.setup(world, balls)

    delta = 1.0
    mode.tick(world, balls, delta)

    # Target should take drain_rate damage
    expected_damage = mode.drain_rate * delta
    assert target.hp == 100 - expected_damage

    assert teammate.hp == 50 - expected_damage
    assert enemy1.hp == 50 + expected_damage * 2
    assert enemy2.hp == 50
