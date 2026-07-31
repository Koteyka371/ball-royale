import pytest
import math
from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, kind):
        self.active = True
        self.duration = 0.0
        self.damage = 0
        self.kind = kind
        self.x = 0
        self.y = 0
        self.radius = 15.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.next_id = 1000

class MockBall:
    def __init__(self, id, x=0, y=0, team="team_a"):
        self.decoy_timer = 0.0
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.base_speed = 200
        self.speed = 2.0
        self.base_damage = 10
        self.radius = 10
        self.damage = 10
        self.is_blinded = False
        self.blindness_timer = 0.0
        self._base_speed_set = True

def test_flashbang_booster_pickup():
    world = MockWorld()
    player = MockBall(1)
    world.balls.append(player)

    booster = MockHazard("flashbang_booster")
    booster.x = 0
    booster.y = 0
    world.boosters.append(booster)

    enemy = MockBall(2, x=200, y=0, team="team_b")
    world.balls.append(enemy)

    action = Action(player, world)
    action._collect_booster(0.016)

    # Booster removed
    assert len(world.boosters) == 0

    # Check enemy is blinded and stunned
    assert enemy.is_blinded
    assert enemy.blindness_timer > 0.0
    assert enemy.is_stunned
    assert getattr(enemy, "stun_timer", 0.0) > 0.0

def test_flashbang_booster_explosion_blindness():
    world = MockWorld()
    decoy = MockBall(2)
    decoy.is_decoy = True
    decoy.decoy_type = "flash"
    world.balls.append(decoy)

    enemy = MockBall(3, x=50, y=0, team="team_b")
    world.balls.append(enemy)

    player = MockBall(4, x=100, y=0, team="team_a")
    world.balls.append(player)

    # Detonate decoy
    decoy.hp = 0

    action = Action(decoy, world)
    action.execute("idle", 0.016)

    assert enemy.is_blinded
    assert enemy.blindness_timer == 3.0

    assert not player.is_blinded
