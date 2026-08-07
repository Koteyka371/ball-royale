import pytest
from ai.game_modes import GAME_MODES
from unittest.mock import MagicMock

class MockBall:
    def __init__(self, id_val, x, y, hp, max_hp, team):
        self.id = id_val
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.team = team
        self.alive = True
        self.ball_type = "player"
        self.low_hp_swap_cooldown = 0.0
        self.traits = []
        self.badges = []
        self.active_perks = []
        self.mutators = []
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.lifesteal = 0.0
        self.cooldown_multiplier = 1.0
        self.experience = 0.0
        self.level = 1
        self.vx = 0.0
        self.vy = 0.0

def test_low_hp_swap_mutator():
    mutator = GAME_MODES["low_hp_swap_mutator"]
    world = MagicMock()

    # b1 is low hp, b2 is low hp enemy, b3 is high hp enemy
    b1 = MockBall(1, 10.0, 10.0, 25.0, 100.0, "TeamA")
    b2 = MockBall(2, 20.0, 20.0, 50.0, 100.0, "TeamB")
    b3 = MockBall(3, 30.0, 30.0, 90.0, 100.0, "TeamB")

    balls = [b1, b2, b3]

    # Tick 1: b1 drops below 30% hp (25/100). Should swap with highest HP enemy (b3)
    mutator.tick(world, balls, delta=0.016)

    # Assert positions swapped
    assert b1.x == 30.0 and b1.y == 30.0
    assert b3.x == 10.0 and b3.y == 10.0

    # b2 should not be moved
    assert b2.x == 20.0 and b2.y == 20.0

    # Cooldowns applied
    assert b1.low_hp_swap_cooldown == 5.0
    assert b3.low_hp_swap_cooldown == 5.0
    assert b2.low_hp_swap_cooldown == 0.0

    # Tick 2: verify cooldown decrements and no further swaps
    b1.hp = 10.0 # still low hp
    mutator.tick(world, balls, delta=1.0)

    assert b1.low_hp_swap_cooldown == 4.0
    assert b3.low_hp_swap_cooldown == 4.0
    assert b1.x == 30.0 and b1.y == 30.0 # no change

def test_low_hp_swap_mutator_gd_exists():
    import os
    with open('src/ai/game_modes.gd', 'r') as f:
        content = f.read()
    assert "class LowHpSwapMutator extends GameMode:" in content
    assert "GAME_MODES['low_hp_swap_mutator'] = LowHpSwapMutator.new()" in content
