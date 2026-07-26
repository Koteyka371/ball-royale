import pytest
from ai.game_modes import GuildBossFightMode

class MockWorld:
    def __init__(self):
        self.arena = None
        self.dead_balls = []
        self.balls = []
        self.entities = []
        self.events = []

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

def test_guild_boss_tier_2_reflection():
    mode = GuildBossFightMode(tier=2)
    world = MockWorld()

    boss = MockBallGuildBoss(1, 500, 500)
    hunter = MockBallGuildBoss(2, 400, 400)
    hunter.hp = 150.0
    hunter.max_hp = 150.0

    balls = [boss, hunter]
    mode.setup(world, balls)

    boss.hp -= 100.0
    mode.tick(world, balls, 1.0)

    assert boss.total_damage_taken == 100.0
    # Hunter starts at 150. setup() multiplies it by 1.5, becoming 225.
    # We deal 100 damage to boss, so 10 is reflected back.
    assert hunter.hp == 215.0

def test_guild_boss_tier_3_spawn():
    mode = GuildBossFightMode(tier=3)
    world = MockWorld()

    boss = MockBallGuildBoss(1, 500, 500)
    hunter = MockBallGuildBoss(2, 400, 400)

    balls = [boss, hunter]
    world.balls = balls
    mode.setup(world, balls)

    # Simulate 10 seconds of time
    for _ in range(int(10.0 / 0.016) + 1):
        mode.tick(world, balls, 0.016)

    minions = [b for b in world.balls if getattr(b, "team", "") == "Boss" and getattr(b, "id", None) != 1]
    assert len(minions) > 0
