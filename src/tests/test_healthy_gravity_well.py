from ai.game_modes import GAME_MODES
from arena.procedural_arena import ProceduralArena, Hazard

class DummyBall:
    def __init__(self, x, y, radius, hp):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.hp = hp
        self.alive = True
        self.team = "test"
        self.ball_type = "normal"
        self.max_speed = 200.0
        self.speed = 200.0

class DummyArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.tick = 0
        self.boosters = []

def test_healthy_gravity_well_pulls_high_hp():
    world = DummyWorld()
    ball = DummyBall(x=700.0, y=700.0, radius=10.0, hp=100.0)

    mode = GAME_MODES["healthy_gravity_well"]
    mode.setup(world, [ball])

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "healthy_gravity_well"

    initial_vel = (ball.vx**2 + ball.vy**2)**0.5

    mode.tick(world, [ball], 0.1)

    final_vel = (ball.vx**2 + ball.vy**2)**0.5

    # Needs to be pulled closer
    assert final_vel > initial_vel

def test_healthy_gravity_well_ignores_low_hp():
    world = DummyWorld()
    ball = DummyBall(x=700.0, y=700.0, radius=10.0, hp=50.0)

    mode = GAME_MODES["healthy_gravity_well"]
    mode.setup(world, [ball])

    initial_vel = (ball.vx**2 + ball.vy**2)**0.5

    mode.tick(world, [ball], 0.1)

    final_vel = (ball.vx**2 + ball.vy**2)**0.5

    # Should not move
    assert final_vel == initial_vel
