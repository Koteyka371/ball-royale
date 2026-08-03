import pytest
from ai.game_modes import BossEscortMode

class MockArena:
    width = 1000
    height = 1000

class MockWorld:
    arena = MockArena()
    def __init__(self):
        self.events = []
    def add_event(self, t, d):
        self.events.append((t, d))

class MockBall:
    def __init__(self, id):
        self.id = id
        self.ball_type = "ai"
        self.alive = True
        self.max_hp = 100
        self.hp = 100
        self.damage = 10
        self.radius = 10
        self.base_speed = 50.0
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0

def test_boss_escort_setup():
    mode = BossEscortMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]
    mode.setup(world, balls)

    assert mode.boss_red is not None
    assert mode.boss_blue is not None
    assert getattr(mode.boss_red, "team") == "Red"
    assert getattr(mode.boss_blue, "team") == "Blue"
    assert getattr(mode.boss_red, "speed") == 20.0

    # 4 normal + 2 bosses
    assert len(balls) == 6

def test_boss_escort_tick():
    mode = BossEscortMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]
    mode.setup(world, balls)

    # Place a blue ball near red boss, to the left
    balls[2].x = mode.boss_red.x - 10
    balls[2].y = mode.boss_red.y
    balls[2].hp = 100

    # Place a red ball near red boss to heal
    balls[0].x = mode.boss_red.x + 10
    balls[0].y = mode.boss_red.y
    balls[0].hp = 50
    balls[0].max_hp = 100

    # Red boss moves right
    start_x = mode.boss_red.x
    mode.tick(world, balls, 1.0)

    assert mode.boss_red.x > start_x

    # Blue ball attacked
    assert balls[2].hp < 100
    # Knockback applied
    assert balls[2].vx < 0

    # Red ball healed
    assert balls[0].hp > 50

def test_boss_escort_winner():
    mode = BossEscortMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]
    mode.setup(world, balls)

    assert mode.check_winner(world, balls) is None

    # Kill blue boss -> Red wins
    mode.boss_blue.alive = False
    assert mode.check_winner(world, balls) == "Red"
