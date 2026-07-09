import pytest
from ai.game_modes import InvisibleWallsMode

class MockBall:
    def __init__(self, x, y, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 20.0
        self.alive = True

class MockAttack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5.0
        self.active = True

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.attacks = []

def test_invisible_walls_attacks():
    mode = InvisibleWallsMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    wall = world.arena.hazards[0]
    wall.x = 500
    wall.y = 500

    # Send attack
    atk = MockAttack(450, 500)
    world.attacks.append(atk)

    mode.tick(world, balls, delta=0.1)

    assert wall.visible == True
    assert wall.reveal_timer > 0
    assert atk.active == False # Attack was absorbed


def test_battle_royale_invisible_walls():
    from ai.game_modes import BattleRoyaleMode
    mode = BattleRoyaleMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    wall = world.arena.hazards[0]
    wall.x = 500
    wall.y = 500

    # Send attack
    atk = MockAttack(450, 500)
    world.attacks.append(atk)

    mode.tick(world, balls, delta=0.1)

    assert wall.visible == True
    assert wall.reveal_timer > 0
    assert atk.active == False
