import pytest
from ai.reverse_friction import ReverseFrictionMode
from ai.action import Action
import math

class MockWorld:
    def __init__(self, game_mode=None):
        self.game_mode = game_mode
        self.tick = 0
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

    def get_nearby_entities(self, ball, radius):
        return []

class MockBall:
    def __init__(self, id, x, y, vx=0.0, vy=0.0, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = alive
        self.ball_type = "player"
        self.hp = 100.0
        self.radius = 10.0
        self.team = "players"

def test_reverse_friction_acceleration():
    mode = ReverseFrictionMode()
    world = MockWorld(game_mode=mode)
    b1 = MockBall(1, 0, 0, vx=100.0, vy=0.0)

    initial_vx = b1.vx

    # Tick should accelerate the ball
    mode.tick(world, [b1], delta=1.0)

    assert b1.vx > initial_vx
    assert b1.vx == initial_vx * (1.0 + mode.acceleration_rate * 1.0)

def test_reverse_friction_collision_damage():
    mode = ReverseFrictionMode()
    world = MockWorld(game_mode=mode)

    b1 = MockBall(1, 0, 0, vx=100.0, vy=0.0)
    b2 = MockBall(2, 5, 0, vx=-50.0, vy=0.0) # They are overlapping (dist 5 < radii sum 20)
    b1.team = "team_a"
    b2.team = "team_b"

    def get_nearby(ball, radius):
        return [b for b in [b1, b2] if b != ball]
    world.get_nearby_entities = get_nearby

    action = Action(b1, world)

    b1_initial_hp = b1.hp
    b2_initial_hp = b2.hp

    action._resolve_collisions()

    # Check if damage was dealt
    # Total speed = 100 + 50 = 150
    # Damage = 150 * 0.1 = 15.0
    expected_damage = 15.0

    assert b1.hp == b1_initial_hp - expected_damage
    assert b2.hp == b2_initial_hp - expected_damage
