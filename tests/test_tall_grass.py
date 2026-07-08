import pytest
from ai.action import Action
from arena.procedural_arena import ProceduralArena, Hazard

class MockBall:
    def __init__(self, x=0, y=0, ball_type="tester"):
        self.x = x
        self.y = y
        self.radius = 15.0
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.inventory = []
        self.base_speed = 100.0

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena()
        self.balls = []

    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball]

def test_tall_grass_damage():
    world = MockWorld()
    ball = MockBall()
    ball.take_damage = lambda dmg: setattr(ball, 'hp', ball.hp - dmg)

    hazard = Hazard(id=1, x=0.0, y=0.0, radius=50.0, kind="tall_grass", damage=5.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    assert ball.hp < 100.0

def test_tall_grass_stealth():
    world = MockWorld()
    ball1 = MockBall(x=0, y=0)
    ball2 = MockBall(x=10, y=0, ball_type="enemy")

    world.balls = [ball1, ball2]

    hazard = Hazard(id=1, x=0.0, y=0.0, radius=50.0, kind="tall_grass", damage=5.0)
    world.arena.hazards.append(hazard)

    action1 = Action(ball1, world)
    enemies1 = action1._get_enemies()
    assert len(enemies1) == 1

    ball1.x = 200.0
    action1 = Action(ball1, world)
    enemies1 = action1._get_enemies()
    assert len(enemies1) == 0

    ball1.x = 0
    ball2.x = 200.0
    action1 = Action(ball1, world)
    enemies1 = action1._get_enemies()
    assert len(enemies1) == 0
