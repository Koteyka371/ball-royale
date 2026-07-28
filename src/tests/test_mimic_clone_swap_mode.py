import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.target_x = x
        self.target_y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.base_speed = 100.0
        self.base_damage_multiplier = 1.0
        self.alive = True
        self.ball_type = "basic"
        self.has_used_mimic_revive = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 9999
        class MockArena:
            def __init__(self):
                self.width = 1000.0
                self.height = 1000.0
        self.arena = MockArena()

def test_mimic_clone_swap_mode():
    mode = GAME_MODES['mimic_clone_swap']
    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    world.balls = [b1]

    # Spawn clone
    mode.tick(world, world.balls, 0.1)

    assert len(world.balls) == 2
    clone = world.balls[1]
    assert getattr(clone, "is_mimic_clone", False)
    assert clone.hp == 100.0

    # Mimic attacks
    b1.active_skill = "shoot"
    mode.tick(world, world.balls, 0.1)
    assert getattr(clone, "active_skill", "") == "shoot"

    # Test random move
    assert clone.vx != 0.0 or clone.vy != 0.0

    # Test revive
    killer = MockBall(2, 500, 500)
    b1.hp = 0.0
    b1.alive = False

    clone.x = 200
    clone.y = 200
    clone.hp = 80
    clone.max_hp = 100

    mode.on_ball_died(world, b1, killer)

    # B1 revived at clone pos
    assert b1.alive == True
    assert b1.x == 200
    assert b1.y == 200
    assert b1.hp == 80
    assert b1.max_hp == 100
    assert getattr(b1, "has_used_mimic_revive", False) == True

    # Clone is dead
    assert clone.alive == False
