import pytest
from ai.action import Action
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y, id="1", team="A"):
        self.x = x
        self.y = y
        self.id = id
        self.team = team
        self.alive = True
        self.stun_timer = 0.0
        self.speed = 10.0
        self.base_speed = 10.0
        self.ball_type = "player"

class MockHazard:
    def __init__(self, x, y, kind="disguised_trap", radius=20.0):
        self.id = 999
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.duration = 15.0
        self.disguised_as = "hp_booster"

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()

def test_disguised_trap_mode_spawns_traps():
    mode = GAME_MODES["disguised_traps"]
    world = MockWorld()
    world.arena.hazards = []
    # simulate enough time to spawn
    mode.tick(world, [], delta=6.0)

    assert len(world.arena.hazards) == 1
    trap = world.arena.hazards[0]
    assert trap.kind == "disguised_trap"
    assert hasattr(trap, "disguised_as")

def test_disguised_trap_triggers():
    world = MockWorld()
    ball = MockBall(100, 100)
    world.balls.append(ball)

    # Place trap near ball
    trap = MockHazard(110, 110, kind="disguised_trap")
    world.arena.hazards.append(trap)

    action = Action(ball, world)
    action.execute("attack", 0.016)

    # Should be triggered
    assert ball.stun_timer >= 3.0
    assert ball.speed == ball.base_speed * 0.1
    assert getattr(trap, "duration", 15.0) == 0.0
