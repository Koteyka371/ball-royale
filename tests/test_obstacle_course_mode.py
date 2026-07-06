import pytest

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self):
        self.id = 1
        self.alive = True
        self.x = 500
        self.y = 500
        self.hp = 100
        self.max_hp = 100
        self.team = "players"
        self.ball_type = "player"

def test_obstacle_course_setup():
    from src.ai.game_modes import ObstacleCourseMode

    mode = ObstacleCourseMode()
    world = MockWorld()
    balls = [MockBall(), MockBall()]

    mode.setup(world, balls)

    # Check if hazards are added
    hazards = world.arena.hazards
    assert len(hazards) == 4

    lasers = [h for h in hazards if getattr(h, "kind", "") == "spinning_laser"]
    assert len(lasers) == 2

    bumpers = [h for h in hazards if getattr(h, "kind", "") == "bumper"]
    assert len(bumpers) == 2

def test_obstacle_course_tick():
    from src.ai.game_modes import ObstacleCourseMode

    mode = ObstacleCourseMode()
    world = MockWorld()
    balls = [MockBall()]

    mode.setup(world, balls)

    # Move past 10 seconds to trigger phase 1 (sinkhole spawn)
    mode.tick(world, balls, delta=10.1)

    sinkholes = [h for h in world.arena.hazards if getattr(h, "kind", "") == "massive_sinkhole"]
    assert len(sinkholes) == 1
    assert sinkholes[0].radius == 100.0

    # Move past 20 seconds to trigger phase 2 (sinkhole expansion)
    mode.tick(world, balls, delta=10.0)

    sinkholes = [h for h in world.arena.hazards if getattr(h, "kind", "") == "massive_sinkhole"]
    assert len(sinkholes) == 1
    assert sinkholes[0].radius == 200.0
