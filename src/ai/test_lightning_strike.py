import pytest
from ai.game_modes import GameMode

class MockArena:
    def __init__(self, is_raining=False):
        self.is_raining = is_raining
        self.hazards = []

class MockWorld:
    def __init__(self, is_raining=False):
        self.arena = MockArena(is_raining)
        self.lightning_strike_timer = 0.0
        self.next_id = 1000
    def add_event(self, name, data):
        pass

class MockBall:
    def __init__(self, id, x, y, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = "normal"
        self.hp = 100.0
        self.speed_multiplier = 1.0
        self.cooldown_multiplier = 1.0
        self.overcharge_timer = 0.0

def test_lightning_strike_logic():
    mode = GameMode()
    world = MockWorld(is_raining=True)
    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 50, 50) # In cluster with b1
    b3 = MockBall(3, 500, 500) # Far away
    balls = [b1, b2, b3]

    import random
    random.seed(42) # Try to force a specific outcome if needed

    # Advance timer to trigger strike
    mode.tick(world, balls, delta=15.0)

    # Force the timer up and force a random chance hit
    # Actually wait, let's just loop a few times to ensure a hit occurs
    hit_occurred = False
    for _ in range(10):
        world.lightning_strike_timer = 15.0
        mode.tick(world, balls, delta=0.1)
        if any(b.hp < 100.0 for b in balls):
            hit_occurred = True
            break

    assert hit_occurred

    # Assert buff is applied for overcharged balls
    for b in balls:
        if b.overcharge_timer > 0:
            assert b.speed_multiplier > 1.0
            assert b.cooldown_multiplier < 1.0

if __name__ == "__main__":
    test_lightning_strike_logic()
    print("Tests passed")
