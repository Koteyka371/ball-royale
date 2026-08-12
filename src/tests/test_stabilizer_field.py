import pytest
from ai.game_modes import WrapAroundMode
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, id, x, y, vx, vy):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 15.0
        self.alive = True
        self.skill_timer = 0.0

class MockArena:
    def __init__(self):
        self.width = 800.0
        self.height = 600.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.next_id = 100

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_deploy_stabilizer_field():
    world = MockWorld()
    ball = MockBall("b1", 100, 100, 0, 0)
    action = Action(ball, world)

    ball.skill = "deploy_stabilizer_field"
    action._use_skill()

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "stabilizer_field"
    assert hazard.x == 100
    assert hazard.y == 100
    assert hazard.radius == 40.0
    assert hazard.owner_id == "b1"

def test_wrap_around_mode_blocks_teleport():
    mode = WrapAroundMode()
    world = MockWorld()

    # Ball moving left to wrap around
    ball = MockBall("b1", 10.0, 300.0, -100.0, 0.0)
    balls = [ball]

    # Place a stabilizer field at the destination (right side)
    field = Hazard(999, 790.0, 300.0, 40.0, "stabilizer_field", 0.0)
    world.arena.hazards.append(field)

    mode.tick(world, balls, 0.016)

    # Normally it would teleport to 784 (800 - 15 - 1)
    # But because of the field, it bounces on the left side
    # Clamped to left side: radius + 1.0 = 16.0
    assert ball.x == 16.0
    # Velocity inverted
    assert ball.vx == 100.0

def test_wrap_around_mode_normal_teleport():
    mode = WrapAroundMode()
    world = MockWorld()

    # Ball moving left to wrap around
    ball = MockBall("b1", 10.0, 300.0, -100.0, 0.0)
    balls = [ball]

    # No stabilizer field at the destination

    mode.tick(world, balls, 0.016)

    # Teleports to right side: arena_width - radius - 1.0 = 800 - 15 - 1 = 784.0
    assert ball.x == 784.0
    # Velocity inverted
    assert ball.vx == 100.0

def test_wrap_around_mode_blocks_teleport_vertical():
    mode = WrapAroundMode()
    world = MockWorld()

    # Ball moving up to wrap around
    ball = MockBall("b1", 400.0, 10.0, 0.0, -100.0)
    balls = [ball]

    # Place a stabilizer field at the destination (bottom side)
    # Target is arena_height - radius - 1 = 584.0
    field = Hazard(999, 400.0, 584.0, 40.0, "stabilizer_field", 0.0)
    world.arena.hazards.append(field)

    mode.tick(world, balls, 0.016)

    # Bounces on top side
    assert ball.y == 16.0
    assert ball.vy == 100.0
