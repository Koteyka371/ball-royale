import pytest
from ai.game_modes import CosmicStormMode

class DummyBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True

class DummyArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()

def test_cosmic_storm_cycle():
    mode = CosmicStormMode()
    world = DummyWorld()
    balls = []

    assert not mode.is_storm_active
    assert mode.storm_timer == 20.0

    # Tick past clear weather
    mode.tick(world, balls, delta=20.1)
    for b in balls: b.hp = 100.0

    assert mode.is_storm_active
    assert len(mode.shelters) >= 3

    # Tick past storm
    mode.tick(world, balls, delta=10.1)

    assert not mode.is_storm_active
    assert len(mode.shelters) == 0

def test_cosmic_storm_damage_outside_shelter():
    mode = CosmicStormMode()
    world = DummyWorld()
    ball = DummyBall(500, 500)
    balls = [ball]

    # Start storm
    mode.tick(world, balls, delta=20.1)
    for b in balls: b.hp = 100.0

    # Move shelters away
    for shelter in mode.shelters:
        shelter["x"] = 9000
        shelter["y"] = 9000

    mode.tick(world, balls, delta=1.0)

    assert ball.hp < 100.0 # Took damage

def test_cosmic_storm_safe_inside_shelter():
    mode = CosmicStormMode()
    world = DummyWorld()
    ball = DummyBall(500, 500)
    balls = [ball]

    # Start storm
    mode.tick(world, balls, delta=20.1)
    for b in balls: b.hp = 100.0

    # Move a shelter onto the ball
    mode.shelters[0]["x"] = 500
    mode.shelters[0]["y"] = 500
    mode.shelters[0]["radius"] = 100
    mode.shelters[0]["capacity"] = 5

    hp_before = ball.hp
    mode.tick(world, balls, delta=1.0)

    assert ball.hp == hp_before # Safe

def test_cosmic_storm_capacity_limit():
    mode = CosmicStormMode()
    world = DummyWorld()

    balls = [DummyBall(500, 500) for _ in range(3)]

    # Start storm
    mode.tick(world, balls, delta=20.1)
    for b in balls: b.hp = 100.0

    # Move a shelter onto the balls, capacity 1
    # Move all other shelters away
    for i, shelter in enumerate(mode.shelters):
        if i == 0:
            shelter["x"] = 500
            shelter["y"] = 500
            shelter["radius"] = 100
            shelter["capacity"] = 1
        else:
            shelter["x"] = 9000
            shelter["y"] = 9000

    mode.tick(world, balls, delta=1.0)

    # Only 1 ball should be safe, 2 should take damage
    safe_count = sum(1 for b in balls if b.hp == 100.0)
    assert safe_count == 1
