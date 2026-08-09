import pytest
from ai.game_modes import SingularityStormMode

class DummyArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.events = []

    def add_event(self, t, d):
        pass

class DummyBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.is_spectator = False
        self.is_dashing = False
        self.inventory = []

def test_singularity_storm_spawns_black_holes():
    mode = SingularityStormMode()
    world = DummyWorld()
    balls = [DummyBall(500, 500)]

    # Tick for 5 seconds to trigger spawn
    for _ in range(501):
        mode.tick(world, balls, delta=0.01)

    assert len(world.arena.hazards) > 0
    assert world.arena.hazards[0].kind == "mini_black_hole"

def test_singularity_storm_pulls_balls():
    mode = SingularityStormMode()
    world = DummyWorld()
    ball = DummyBall(450, 500)
    balls = [ball]

    # Force spawn a black hole
    mode.event_timer = 5.0
    mode.tick(world, balls, delta=1.0) # spawns BH

    # Manually set BH pos to (500, 500)
    world.arena.hazards[0].x = 500
    world.arena.hazards[0].y = 500
    world.arena.hazards[0].pull_radius = 300
    world.arena.hazards[0].pull_strength = 400.0

    # Initial distance is 50
    initial_x = ball.x
    mode.tick(world, balls, delta=0.1)

    # Should be pulled towards 500
    assert ball.x > initial_x

def test_singularity_storm_dashing_prevents_pull():
    mode = SingularityStormMode()
    world = DummyWorld()
    ball = DummyBall(450, 500)
    ball.is_dashing = True
    balls = [ball]

    # Force spawn a black hole at (500, 500)
    mode.event_timer = 5.0
    mode.tick(world, balls, delta=1.0) # spawns BH

    world.arena.hazards[0].x = 500
    world.arena.hazards[0].y = 500
    world.arena.hazards[0].pull_radius = 300
    world.arena.hazards[0].pull_strength = 400.0

    initial_x = ball.x
    mode.tick(world, balls, delta=0.1)

    # Should NOT be pulled
    assert ball.x == initial_x

def test_singularity_storm_gravity_boots_prevents_pull():
    mode = SingularityStormMode()
    world = DummyWorld()
    ball = DummyBall(450, 500)
    ball.inventory = ["gravity_boots"]
    balls = [ball]

    # Force spawn a black hole at (500, 500)
    mode.event_timer = 5.0
    mode.tick(world, balls, delta=1.0) # spawns BH

    world.arena.hazards[0].x = 500
    world.arena.hazards[0].y = 500
    world.arena.hazards[0].pull_radius = 300
    world.arena.hazards[0].pull_strength = 400.0

    initial_x = ball.x
    mode.tick(world, balls, delta=0.1)

    # Should NOT be pulled
    assert ball.x == initial_x
