import pytest
from ai.game_modes import WallLeapersMode
from arena.procedural_arena import Hazard

class MockArena:
    def __init__(self):
        self.hazards = []
        self.min_x = 0.0
        self.max_x = 1000.0
        self.min_y = 0.0
        self.max_y = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.speed = 100.0
        self.hp = 100.0
        self.alive = True

def test_wall_leapers_spawn():
    mode = WallLeapersMode()
    world = MockWorld()
    balls = []

    # Tick past spawn timer
    mode.tick(world, balls, delta=6.1)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "wall_leaper"
    assert hazard.state == "wall"

def test_wall_leapers_leap_and_attach():
    mode = WallLeapersMode()
    mode.spawn_timer = 10.0 # Prevent natural spawn
    world = MockWorld()

    h = Hazard(id=1, x=500.0, y=500.0, radius=15.0, kind="wall_leaper", damage=30.0)
    setattr(h, "state", "wall")
    setattr(h, "fuse_timer", 3.0)
    setattr(h, "target_id", None)
    world.arena.hazards.append(h)

    ball = MockBall(1, 550.0, 500.0) # within 150 units
    balls = [ball]

    # Tick 1: detects ball, enters "leaping" state
    mode.tick(world, balls, delta=0.1)
    assert h.state == "leaping"
    assert h.target_id == 1

    # Tick 2: finish leaping
    mode.tick(world, balls, delta=0.5)
    assert h.state == "attached"
    assert h.x == ball.x
    assert h.y == ball.y

def test_wall_leapers_slow_and_explode():
    mode = WallLeapersMode()
    mode.spawn_timer = 10.0 # Prevent natural spawn
    world = MockWorld()

    h = Hazard(id=1, x=500.0, y=500.0, radius=15.0, kind="wall_leaper", damage=30.0)
    setattr(h, "state", "attached")
    setattr(h, "fuse_timer", 1.0)
    setattr(h, "target_id", 1)
    world.arena.hazards.append(h)

    ball = MockBall(1, 500.0, 500.0)
    balls = [ball]

    # Tick 1: apply slow, tick down fuse
    mode.tick(world, balls, delta=0.5)
    assert h.fuse_timer == pytest.approx(0.5)
    assert ball.speed == pytest.approx(50.0) # Slowed from 100 to 50
    assert len(world.arena.hazards) == 1

    # Move ball, ensure hazard follows
    ball.x = 600.0
    ball.y = 600.0
    mode.tick(world, balls, delta=0.2)
    assert h.x == 600.0
    assert h.y == 600.0

    # Tick 2: fuse expires, explode
    mode.tick(world, balls, delta=0.4)
    assert ball.hp == pytest.approx(70.0) # 100 - 30 damage
    assert len(world.arena.hazards) == 0 # Hazard destroyed

    assert ball.speed == pytest.approx(100.0) # Speed restored