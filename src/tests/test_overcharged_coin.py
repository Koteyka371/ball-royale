import pytest
from ai.game_modes import BlackMarketMode
from ai.action import Action
import copy

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100
        self.y = 100
        self.radius = 15
        self.currency = 0
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0

class MockWorld:
    def __init__(self):
        self.currency_pickups = [{"x": 100, "y": 100, "type": "overcharged_coin"}]
        self.black_markets = []
        self.arena = type('Arena', (), {'width': 1000, 'height': 1000})()

def test_overcharged_currency_debuff():
    world = MockWorld()
    mode = BlackMarketMode()
    ball = MockBall()

    mode.tick(world, [ball], 0.1)

    assert ball.currency == 5
    assert hasattr(ball, "overcharged_coin_debuff_timer")
    assert ball.overcharged_coin_debuff_timer == 3.0

    action = Action(ball, world)

    # Run _update_skill_timer which applies debuffs
    action._update_skill_timer(0.1)

    assert ball.speed == 50.0
    assert ball.overcharged_coin_debuff_timer == 2.9
