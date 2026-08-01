import math
import random
from ai.action import Action
from ai.game_modes import MirrorCloneEventMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.events = []
        self.next_id = 9999

    def add_event(self, type, data):
        self.events.append({'type': type, 'data': data})

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.radius = 15.0
        self.team = "team1"
        self.ball_type = "default"
        self.speed = 10.0
        self.is_mirror_clone = False
        self.is_decoy = False
        self.is_decoy_clone = False
        self.is_illusion = False

def test_mirror_clone_spawns():
    mode = MirrorCloneEventMode()
    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    world.balls.append(b1)

    # Event timer needs to run down
    mode.tick(world, world.balls, delta=21.0)

    assert mode.is_cloned is True
    assert len(world.balls) == 2

    clone = world.balls[1]
    assert clone.is_mirror_clone is True
    assert clone.owner_id == b1.id
    assert clone.x == b1.x
    assert clone.y == b1.y

def test_mirror_clone_mimics_reverse():
    mode = MirrorCloneEventMode()
    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    b1.vx = 50.0
    b1.vy = -30.0
    world.balls.append(b1)

    mode.tick(world, world.balls, delta=21.0)

    clone = world.balls[1]

    action = Action(clone, world) # Fix arguments: ball first, world second
    action.execute("idle", 1.0)

    assert clone.vx == -50.0
    assert clone.vy == 30.0

    assert clone.x == 100.0 - 50.0
    assert clone.y == 100.0 + 30.0

def test_mirror_clone_damage_transfer():
    mode = MirrorCloneEventMode()
    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    world.balls.append(b1)

    mode.tick(world, world.balls, delta=21.0)

    clone = world.balls[1]

    # Apply damage to clone
    clone.hp -= 30.0

    mode.tick(world, world.balls, delta=0.016)

    assert b1.hp == 70.0

    # Apply more damage to clone, should kill original
    clone.hp -= 80.0

    mode.tick(world, world.balls, delta=0.016)

    assert b1.hp <= 0.0
    assert b1.alive is False
