import pytest
import math
from unittest.mock import MagicMock
from arena.procedural_arena import ProceduralArena
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team=1):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.speed = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.radius = 10.0
        self.memory = {}
        self.is_blinded = False
        self.blindness_timer = 0.0
        self.inventory = []
        self.ball_type = "player"

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(2000, 2000)
        self.arena.hazards = []
        self.balls = []
        self.boosters = []
        self.events = []

    def _deal_damage(self, target, source):
        pass

def test_ghost_mode_booster_collect():
    world = MockWorld()
    ball = MockBall(1, 100, 100, 1)
    world.balls.append(ball)

    booster = MagicMock()
    booster.kind = "ghost_mode_booster"
    booster.x = 100
    booster.y = 100
    booster.radius = 15
    booster.ball_type = "booster"
    booster.active = True
    world.boosters.append(booster)

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    assert getattr(ball, "ghost_mode_timer", 0.0) == 5.0
    assert getattr(ball, "intangible", False) == True
    assert getattr(ball, "ghost_mode_active", False) == True
    assert booster not in world.boosters

def test_ghost_mode_breaks_on_attack():
    world = MockWorld()
    ball = MockBall(1, 100, 100, 1)
    ball.ghost_mode_timer = 3.0
    ball.intangible = True
    ball.ghost_mode_active = True
    world.balls.append(ball)

    enemy = MockBall(2, 200, 200, 2)
    world.balls.append(enemy)

    action = Action(ball, world)
    action.execute("attack", 1.0)

    assert getattr(ball, "ghost_mode_timer", 0.0) == 0.0
    assert getattr(ball, "intangible", False) == False
    assert getattr(ball, "ghost_mode_active", False) == False

def test_ghost_mode_immune_to_non_energy():
    world = MockWorld()
    ball = MockBall(1, 100, 100, 1)
    ball.ghost_mode_timer = 3.0
    ball.intangible = True
    ball.ghost_mode_active = True
    world.balls.append(ball)

    proj = MagicMock()
    proj.ball_type = "projectile"
    proj.is_energy = False
    proj.damage_type = "physical"
    proj.damage = 10.0

    action = Action(ball, world)
    action._attempt_damage(proj, ball)

    assert getattr(ball, "hp", 100.0) == 100.0
