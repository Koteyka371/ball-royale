import pytest
from ai.game_modes import GameMode, GAME_MODES

class MockBall:
    def __init__(self, x, y, team, hp=100.0, speed=100.0, base_speed=100.0):
        self.x = x
        self.y = y
        self.team = team
        self.hp = hp
        self.max_hp = 100.0
        self.speed = speed
        self.base_speed = base_speed
        self.radius = 20.0
        self.alive = True
        self.ball_type = "test"
        self.is_spectator = False
        self.take_damage_called = 0

    def take_damage(self, amount, source):
        self.hp -= amount
        self.take_damage_called += 1

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_color_control_mode():
    mode = GAME_MODES.get("color_control")
    assert mode is not None

    world = MockWorld()
    b1 = MockBall(100, 100, "Red")
    b2 = MockBall(200, 200, "Blue")
    balls = [b1, b2]

    # Tick past the 0.1s threshold to spawn trails
    mode.tick(world, balls, 0.11)

    # Should have 2 hazards
    assert len(world.arena.hazards) == 2

    # Fast forward: b1 stays on Red trail, b2 stays on Blue trail
    # Both should gain speed and regen
    for _ in range(5):
        mode.tick(world, balls, 0.05)

    assert b1.speed > 100
    assert b1.hp >= 100
    assert b2.speed > 100

    # Move b2 onto b1's trail (Red)
    b2.x = 100
    b2.y = 100
    for _ in range(5):
        mode.tick(world, balls, 0.05)

    # b2 should lose speed and take damage
    assert b2.speed < 100
    assert b2.hp < 100

    # Check winner based on territory
    mode.timer = 0.0
    winner = mode.check_winner(world, balls)
    assert winner in ["Red", "Blue", "Draw"]
