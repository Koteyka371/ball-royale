import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/')))
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
    def __init__(self, id, x, y):
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
        self.ball_type = "normal"
        self.alive = True

def test_guild_boss_fight_mode_setup():
    mode = GuildBossFightMode()
    world = MockWorld()

    boss = MockBallGuildBoss(1, 0, 0)
    hunter1 = MockBallGuildBoss(2, 0, 0)
    hunter2 = MockBallGuildBoss(3, 0, 0)

    balls = [boss, hunter1, hunter2]
    mode.setup(world, balls)

    assert boss.team == "Boss"
    assert boss.max_hp == 10000000.0
    assert boss.hp == 10000000.0
    assert boss.total_damage_taken == 0.0
    assert mode.boss_id == 1

    assert hunter1.team == "Hunters"
    assert hunter1.max_hp == 150.0

def test_guild_boss_fight_mode_tick():
    mode = GuildBossFightMode()
    world = MockWorld()

    boss = MockBallGuildBoss(1, 500, 500)
    hunter = MockBallGuildBoss(2, 500, 400) # Dist = 100, within pull_radius
    far_hunter = MockBallGuildBoss(3, 100, 100) # Dist > 300, outside pull_radius

    balls = [boss, hunter, far_hunter]
    mode.setup(world, balls)

    # Simulate damage
    boss.hp -= 500.0

    mode.tick(world, balls, 1.0)

    # Boss should heal and track damage
    assert boss.hp == boss.max_hp
    assert boss.total_damage_taken == 500.0

    # Hunter should be pulled
    assert hunter.vy > 0.0

    # Far hunter should not be pulled
    assert far_hunter.vx == 0.0
    assert far_hunter.vy == 0.0

class MockGuildManager:
    def __init__(self):
        self.recorded_damage = 0.0

    def record_boss_damage(self, guild_name, damage, week_id):
        self.recorded_damage = damage

def test_guild_boss_fight_mode_end_match():
    gm = MockGuildManager()
    mode = GuildBossFightMode(guild_name="TestGuild", guild_manager=gm)
    world = MockWorld()

    boss = MockBallGuildBoss(1, 500, 500)
    balls = [boss]
    mode.setup(world, balls)

    boss.hp -= 1000.0
    mode.tick(world, balls, 1.0)

    assert boss.total_damage_taken == 1000.0
    mode.end_match(world, balls)

    assert gm.recorded_damage == 1000.0
