import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/')))
from ai.game_modes import GuildBossFightMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBallGuildBoss:
    def __init__(self, id, x, y, ball_type="normal"):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.radius = 10.0
        self.base_speed = 100.0
        self.mass = 1.0
        self.team = ""
        self.ball_type = ball_type
        self.traits = []
        self.alive = True

def test_guild_boss_weakness_week_1():
    mode = GuildBossFightMode(week_id="week_1")
    world = MockWorld()

    # Week 1 weakness should be elements[0] -> "fire"
    boss = MockBallGuildBoss(1, 0, 0)
    hunter_fire = MockBallGuildBoss(2, 0, 0, ball_type="fire_mage")
    hunter_water = MockBallGuildBoss(3, 0, 0, ball_type="water_mage")

    balls = [boss, hunter_fire, hunter_water]
    mode.setup(world, balls)

    assert mode.boss_weakness == "fire"
    assert boss.boss_weakness == "fire"

    # Deal 100 damage
    boss.hp -= 100.0
    mode.tick(world, balls, 1.0)

    # Since hunter_fire is alive, damage taken should be multiplied by 1.5
    assert boss.total_damage_taken == 150.0

def test_guild_boss_weakness_no_weakness_hunter():
    mode = GuildBossFightMode(week_id="week_2")
    world = MockWorld()

    # Week 2 weakness should be elements[1] -> "water"
    boss = MockBallGuildBoss(1, 0, 0)
    hunter_fire = MockBallGuildBoss(2, 0, 0, ball_type="fire_mage")

    balls = [boss, hunter_fire]
    mode.setup(world, balls)

    assert mode.boss_weakness == "water"
    assert boss.boss_weakness == "water"

    # Deal 100 damage
    boss.hp -= 100.0
    mode.tick(world, balls, 1.0)

    # Since no hunter has the "water" trait, damage is 1x
    assert boss.total_damage_taken == 100.0
