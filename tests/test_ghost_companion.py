import pytest
from ai.ghost_companion import GhostCompanionMode

class MockBall:
    def __init__(self, id_val, x, y, hp=100.0, team="red"):
        self.id = id_val
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = hp
        self.max_hp = 100.0
        self.alive = hp > 0
        self.team = team
        self.ball_type = "player"
        self.speed = 100.0
        self.base_speed = 100.0
        self.is_ghost = False

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockWorld:
    def __init__(self):
        self.dead_balls = []

def test_ghost_companion_spawn():
    mode = GhostCompanionMode()
    world = MockWorld()

    b1 = MockBall(1, 0, 0, hp=0, team="red")
    b2 = MockBall(2, 100, 100, hp=100, team="blue")
    balls = [b1, b2]

    mode.setup(world, balls)
    mode.tick(world, balls, delta=1.0)

    # b1 should be revived as a ghost
    assert b1.alive
    assert b1.is_ghost
    assert b1.hp == 50.0
    assert b1.speed == 150.0
    assert b1.ghost_target_id is not None # Should target b2

def test_ghost_companion_buff_debuff():
    mode = GhostCompanionMode()
    world = MockWorld()

    # Ghost attached to enemy
    g1 = MockBall(1, 100, 100, hp=50, team="red")
    g1.is_ghost = True
    g1.ghost_target_id = 2

    # Enemy target
    b2 = MockBall(2, 100, 100, hp=100, team="blue")

    # Ghost attached to teammate
    g3 = MockBall(3, 200, 200, hp=50, team="green")
    g3.is_ghost = True
    g3.ghost_target_id = 4

    # Teammate target
    b4 = MockBall(4, 200, 200, hp=90, team="green")

    balls = [g1, b2, g3, b4]
    mode.setup(world, balls)
    mode.tick(world, balls, delta=1.0)

    # b2 (enemy) should be debuffed and take damage
    assert b2.speed < b2.base_speed
    assert b2.hp < 100.0

    # b4 (teammate) should be buffed and heal
    assert b4.speed > b4.base_speed
    assert b4.hp > 90.0

def test_ghost_companion_check_winner():
    mode = GhostCompanionMode()
    world = MockWorld()

    # Only team blue is alive (red is ghost)
    b1 = MockBall(1, 0, 0, hp=50, team="red")
    b1.is_ghost = True

    b2 = MockBall(2, 100, 100, hp=100, team="blue")

    balls = [b1, b2]

    winner = mode.check_winner(world, balls)
    assert winner == "blue"
