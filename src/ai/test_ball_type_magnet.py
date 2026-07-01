import pytest
from ai.ball_types_magnet import Magnet
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.radius = 10
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.traits = []
        self.stamina = 100
        self.max_stamina = 100
        self.speed = 100
        self.base_speed = 100
        self.is_dashing = False

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball]

def test_magnet_pull_booster():
    ball = Magnet(1)
    ball.x = 0
    ball.y = 0

    world = MockWorld()
    world.balls.append(ball)

    booster = Hazard(1, 100, 0, 15, "booster", 0)
    world.arena.hazards.append(booster)

    action = Action(ball, world)
    action._update_skill_timer(1.0)

    # Booster should be pulled closer (x decreases)
    assert booster.x < 100

def test_magnet_pull_smaller_entity():
    ball = Magnet(1)
    ball.x = 0
    ball.y = 0
    ball.radius = 20

    smaller = MockBall(2, 100, 0)
    smaller.radius = 10

    world = MockWorld()
    world.balls.append(ball)
    world.balls.append(smaller)

    action = Action(ball, world)
    action._update_skill_timer(1.0)

    # Smaller entity should be pulled closer
    assert smaller.x < 100

def test_magnet_magnetic_repel():
    ball = Magnet(1)
    ball.x = 0
    ball.y = 0

    enemy = MockBall(2, 10, 0)

    world = MockWorld()
    world.balls.append(ball)
    world.balls.append(enemy)

    action = Action(ball, world)
    action.execute("magnetic_repel", 1.0)

    # Enemy pushed away
    assert enemy.x > 10
