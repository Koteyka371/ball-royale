import pytest
import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []
        self.items = []

class MockBall:
    def __init__(self, x, y, team, id, inventory=None):
        self.x = x
        self.y = y
        self.team = team
        self.id = id
        self.vx = 0.0
        self.vy = 0.0
        self.skill = "grapple"
        self.active_skill = "grapple"
        self.SKILL_COOLDOWN = 5.0
        self.skill_timer = 0.0
        self.hp = 100
        self.alive = True
        self.state_history = []
        self.charge_level = 100
        self.inventory = inventory or []
        self.ball_type = "player"

def test_grapple_chain_default():
    world = MockWorld()

    player = MockBall(500, 500, team=-1, id="p1")
    enemy1 = MockBall(500, 450, team=-2, id="e1")
    enemy2 = MockBall(500, 400, team=-2, id="e2")
    enemy3 = MockBall(500, 350, team=-2, id="e3")
    enemy4 = MockBall(500, 300, team=-2, id="e4")

    world.balls = [player, enemy1, enemy2, enemy3, enemy4]

    action = Action(player, world)
    action._use_skill()

    assert enemy1.y == 490.0 # (dx=0, dy=-50. dist=50. dy/dist=-1. y -= -1 * 40 => y += 40 => 490)
    assert enemy2.y > 400.0 # Chained target is pulled by 200 distance
    assert enemy3.y == 350.0
    assert enemy4.y == 300.0

def test_grapple_chain_with_item():
    world = MockWorld()

    player = MockBall(500, 500, team=-1, id="p1", inventory=["grapple_chain_item"])
    enemy1 = MockBall(500, 450, team=-2, id="e1")
    enemy2 = MockBall(500, 400, team=-2, id="e2")
    enemy3 = MockBall(500, 350, team=-2, id="e3")
    enemy4 = MockBall(500, 300, team=-2, id="e4")

    world.balls = [player, enemy1, enemy2, enemy3, enemy4]

    action = Action(player, world)
    action._use_skill()

    assert enemy1.y == 490.0
    assert enemy2.y > 400.0
    assert enemy3.y > 350.0
    assert enemy4.y > 300.0
