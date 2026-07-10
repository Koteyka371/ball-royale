import pytest
import math
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.id = 1
        self.x = x
        self.y = y
        self.team = "test_team"
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.radius = 10.0
        self.base_speed = 0.0 # prevent wander from adding random x/y
        self.speed = 0.0
        self.damage = 10.0
        self.is_orbiting_accelerator = False
        self.is_flying = False
        self.inventory = []
        self.vx = 0
        self.vy = 0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = type('Arena', (), {})()
        self.arena.hazards = []
        self.arena.is_night = False
        self.arena.is_foggy = False
        self.arena.is_eclipse = False
        self.game_mode = type('Mode', (), {'name': 'default'})()
        self.arena.safe_zone_center = (500, 500)
        self.arena.safe_zone_radius = 5000
        self.arena.update_zone = lambda *args: None
        self.arena.clamp_position = lambda x, y, r: (x, y, False)
        self.width = 1000
        self.height = 1000
        self.tick = 1
        self.time = 0.0
        self.events = []

def test_vortex_orbit():
    ball = MockBall(x=50.0, y=0.0) # Start to the right of origin
    world = MockWorld()
    world.balls.append(ball)

    # Vortex at origin
    vortex = Hazard(id=1, x=0.0, y=0.0, radius=200.0, kind="vortex", damage=0.0)
    world.arena.hazards.append(vortex)

    action = Action(ball, world)

    # disable the movement part of action
    action._move = lambda *args: None

    action.execute("idle", 0.1) # delta=0.1
    # dx = 0 - 50 = -50
    # dy = 0 - 0 = 0
    # dist = 50
    # nx = -1, ny = 0
    # px = 0, py = -1
    # pull_strength = 50.0 * 0.1 = 5
    # orbit_strength = 150.0 * 0.1 = 15
    # x += -1 * 5 + 0 = -5 => 45
    # y += 0 + -1 * 15 = -15 => -15

    assert math.isclose(ball.x, 45.0, abs_tol=0.1)
    assert math.isclose(ball.y, -15.0, abs_tol=0.1)
