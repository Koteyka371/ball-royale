import pytest
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, id=1, ball_type="normal", hp=100.0, x=0.0, y=0.0):
        self.id = id
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = 100.0
        self.x = x
        self.y = y
        self.radius = 10.0
        self.speed_buff_timer = 0.0
        self.geyser_immunity_timer = 0.0
        self.stun_timer = 0.0
        self.base_speed = 10.0
        self.speed = 10.0
        self.alive = True

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.time = 0.0
        self.tick = 0
    def _deal_damage(self, attacker, target, dmg=0.0):
        target.hp -= dmg

def test_geyser_eruption_damage():
    world = MockWorld()
    world.time = 1.0 # Within the 1.5s eruption window

    ball = MockBall(id=1, ball_type="fire_elemental", hp=100.0)
    world.balls.append(ball)

    geyser = Hazard(id=1, x=0.0, y=0.0, radius=50.0, kind="geyser", damage=10.0)
    world.arena.hazards.append(geyser)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.hp < 100.0
    assert ball.stun_timer >= 1.0
    assert ball.geyser_immunity_timer > 0.0

def test_geyser_buff():
    world = MockWorld()
    world.time = 1.0 # Within the 1.5s eruption window

    ball = MockBall(id=1, ball_type="water_elemental", hp=50.0)
    world.balls.append(ball)

    geyser = Hazard(id=1, x=0.0, y=0.0, radius=50.0, kind="geyser", damage=10.0)
    world.arena.hazards.append(geyser)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.hp > 50.0 # Healed
    assert ball.stun_timer >= 1.0
    assert ball.speed_buff_timer > 0.0
    assert ball.geyser_immunity_timer > 0.0

def test_geyser_no_eruption():
    world = MockWorld()
    world.time = 3.0 # Outside the 1.5s eruption window

    ball = MockBall(id=1, ball_type="fire_elemental", hp=100.0)
    world.balls.append(ball)

    geyser = Hazard(id=1, x=0.0, y=0.0, radius=50.0, kind="geyser", damage=10.0)
    world.arena.hazards.append(geyser)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.hp == 100.0
    assert ball.stun_timer == 0.0
    assert ball.geyser_immunity_timer == 0.0
