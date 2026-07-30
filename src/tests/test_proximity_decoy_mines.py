import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.next_id = 100

class MockBall:
    def __init__(self, x, y, ball_type="basic"):
        self.id = 1
        self.x = x
        self.y = y
        self.radius = 20.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = ball_type

def test_proximity_decoy_mines_setup():
    mode = GAME_MODES['proximity_decoy_mines']
    world = MockWorld()
    balls = [MockBall(500, 500)]

    mode.setup_done = False
    mode.setup(world, balls)

    decoys = [b for b in world.balls if getattr(b, "ball_type", "") == "decoy_mine"]
    assert len(decoys) == mode.decoy_count

    for d in decoys:
        assert d.state == "dormant"
        assert d.is_decoy == True

def test_proximity_decoy_mines_trigger():
    mode = GAME_MODES['proximity_decoy_mines']
    world = MockWorld()
    balls = []

    mode.setup_done = False
    mode.setup(world, balls)

    decoys = [b for b in world.balls if getattr(b, "ball_type", "") == "decoy_mine"]
    decoy = decoys[0]

    # Place a real ball near the decoy
    real_ball = MockBall(decoy.x + mode.trigger_radius - 10, decoy.y)
    world.balls.append(real_ball)

    mode.tick(world, world.balls, 0.1)

    assert decoy.state == "active"
    assert math.hypot(decoy.vx, decoy.vy) > 0 # Should have movement now

def test_proximity_decoy_mines_detonate():
    mode = GAME_MODES['proximity_decoy_mines']
    world = MockWorld()
    balls = []

    mode.setup_done = False
    mode.setup(world, balls)

    decoys = [b for b in world.balls if getattr(b, "ball_type", "") == "decoy_mine"]
    decoy = decoys[0]

    # Manually activate it and place a real ball exactly on it
    decoy.state = "active"
    real_ball = MockBall(decoy.x, decoy.y)
    world.balls.append(real_ball)

    initial_hp = real_ball.hp

    mode.tick(world, world.balls, 0.1)

    assert decoy.alive == False
    assert real_ball.hp == max(0.0, initial_hp - mode.explosion_damage)

    # Check visual event
    explosion_events = [e for e in world.events if e['type'] == 'visual_effect' and e['data']['type'] == 'explosion']
    assert len(explosion_events) > 0
