import pytest
from ai.game_modes import UnstablePayloadMode
import math

class DummyArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class DummyBall:
    def __init__(self, id, x, y, radius=15.0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.alive = True
        self.ball_type = "normal"
        self.team = "Red"
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.max_hp = 100.0

def test_unstable_payload_spawn_and_expand():
    mode = UnstablePayloadMode()
    world = DummyWorld()
    balls = [DummyBall(1, 100, 100)]

    # Spawn tick
    mode.spawn_timer = 0.0
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 1
    h = world.arena.hazards[0]
    assert h.kind == "unstable_payload"
    assert h.x == 500.0
    assert h.y == 500.0

    # Expand tick
    initial_radius = h.radius
    mode.tick(world, balls, 1.0)
    assert h.radius > initial_radius

def test_unstable_payload_radiation_and_explosion():
    mode = UnstablePayloadMode()
    world = DummyWorld()

    # b1 is near payload, b2 is far
    b1 = DummyBall(1, 520, 500)
    b2 = DummyBall(2, 900, 900)
    balls = [b1, b2]

    mode.spawn_timer = 0.0
    mode.tick(world, balls, 0.1)
    h = world.arena.hazards[0]

    # Radiation tick
    mode.tick(world, balls, 1.0)

    assert b1.hp < 100.0
    assert b2.hp == 100.0

    # Explode tick
    h.mass_timer = 15.0
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 0
    assert not b1.alive
    assert b1.hp == 0.0

def test_unstable_payload_push():
    mode = UnstablePayloadMode()
    world = DummyWorld()

    # Ball hits payload
    b1 = DummyBall(1, 480, 500)
    b1.vx = 500.0
    balls = [b1]

    mode.spawn_timer = 0.0
    mode.tick(world, balls, 0.1)
    h = world.arena.hazards[0]

    # Tick for collision logic - ball was already overlapping at spawn so it pushes it in the first tick!
    assert h.vx > 0.0 # Payload pushed right
