import pytest
from src.ai.action import Action
from tests.simulate_battle import Ball, Booster, BattleSimulation

class MockEntity:
    def __init__(self, x, y, hp=100, ball_type="default"):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100
        self.ball_type = ball_type

    def take_damage(self, amount):
        self.hp -= amount

class MockWorld:
    def __init__(self):
        self.boosters = []

    def _collect_booster(self, ball, booster):
        self.boosters.remove(booster)

def test_link_booster():
    world = MockWorld()

    ball = MockEntity(0, 0, hp=50, ball_type="player")
    enemy = MockEntity(100, 100, hp=100, ball_type="enemy") # Move further so it doesn't interrupt collect

    booster = MockEntity(5, 5, hp=0, ball_type="booster")
    booster.kind = "link_booster"
    booster.radius = 15

    world.boosters = [booster]

    action = Action(ball, world)
    action._get_enemies = lambda: [enemy]
    action._get_boosters = lambda: world.boosters

    # Needs to be close enough to collect
    ball.x = 4.5
    ball.y = 4.5

    action.execute("collect_booster", 0.0) # Delta 0 so timer doesn't tick down immediately

    assert getattr(ball, "link_booster_timer", 0) == 5.0
    assert getattr(ball, "link_booster_target", None) == enemy
    assert booster not in world.boosters

    action.execute("idle", 0.5)

    assert ball.link_booster_timer == 4.5
    assert enemy.hp == 90.0 # 20 per sec * 0.5 sec = 10 drain
    assert ball.hp == 60.0 # 50 + 10 = 60
