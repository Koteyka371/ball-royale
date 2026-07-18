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
    assert clone.base_damage_multiplier == 0.5
    assert clone.hp == 100.0

    # Mimic input
    b1.vx = 50.0
    b1.vy = -50.0
    mode.tick(world, world.balls, 0.1)

    assert clone.vx == 50.0
    assert clone.vy == -50.0

    # Test double damage taken
    clone.hp = 90.0 # Took 10 damage
    mode.tick(world, world.balls, 0.1)
    assert clone.hp == 80.0 # Extra 10 damage taken to make it double

    # Test revive
    killer = MockBall(2, 500, 500)
    b1.hp = 0.0
    b1.alive = False

    # Store clone pos for reference
    cx, cy = clone.x, clone.y
    mode.on_ball_died(world, b1, killer)

    # B1 revived at clone pos with halved stats
    assert b1.alive == True
    assert b1.x == cx
    assert b1.y == cy
    assert b1.max_hp == 50.0
    assert b1.hp == 50.0
    assert b1.base_damage_multiplier == 0.5
    assert getattr(b1, "has_used_mimic_revive", False) == True

    # Clone is dead
    assert clone.alive == False
