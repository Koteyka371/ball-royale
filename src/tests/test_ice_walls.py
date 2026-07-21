import pytest
from ai.action import Action
import math

class MockGameMode:
    def __init__(self):
        self.name = "Normal"
        self.tick_timer = 0.0

    def tick(self, world, balls, delta):
        self.tick_timer += delta

class MockArena:
    def __init__(self):
        self.hazards = []
        self.boundary_states = {"top": "ice", "bottom": "ice", "left": "ice", "right": "ice"}
        self.boundary_health = {"top": 100.0, "bottom": 1000.0, "left": 1000.0, "right": 1000.0}

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.game_mode = MockGameMode()

class MockBall:
    def __init__(self, x, y):
        self.id = "test_ball"
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 20.0
        self.hp = 100
        self.alive = True
        self.mass = 1.0
        self.stutter_timer = 0.0
        self._cooldowns = {}
        self.is_stealthed = False
        self.stealth_timer = 0.0
        self.max_hp = 100
        self.is_decoy = False
        self.is_illusion = False

def test_ice_wall_break():
    world = MockWorld()
    # Position right at top wall
    ball = MockBall(500, 10)
    # High speed upwards
    ball.vx = 0
    ball.vy = -1000

    world.balls.append(ball)

    action = Action(ball, world)
    action.execute('aggressive', 0.1)

    assert world.arena.boundary_health["top"] < 100.0
    print(f"Top wall health: {world.arena.boundary_health['top']}")
    print(f"Top wall state: {world.arena.boundary_states['top']}")
