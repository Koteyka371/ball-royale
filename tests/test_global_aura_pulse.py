import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 2000.0
        self.height = 2000.0
        self.is_night = False
        self.is_lunar_eclipse = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.events = []

class MockBall:
    def __init__(self, id, team="red", ball_type="warrior", x=0.0, y=0.0, hp=100.0, max_hp=100.0):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.aura_booster_timer = 0.0
        self.vampiric_aura_timer = 0.0
        self.aura_inversion_timer = 0.0

def test_global_aura_pulse_friendly():
    mode = GAME_MODES["global_aura_pulse"]
    world = MockWorld()

    b1 = MockBall(1, team="red")
    b1.aura_booster_timer = 10.0

    b2 = MockBall(2, team="red") # Friendly target
    b3 = MockBall(3, team="blue") # Enemy

    world.balls = [b1, b2, b3]
    mode.timer = 0.0 # Force trigger

    mode.tick(world, world.balls, 0.016)

    # b2 should have received the aura buff
    assert b2.aura_booster_timer == 5.0
    # b3 should not
    assert b3.aura_booster_timer == 0.0

def test_global_aura_pulse_reversed():
    mode = GAME_MODES["global_aura_pulse"]
    world = MockWorld()

    b1 = MockBall(1, team="red")
    b1.vampiric_aura_timer = 10.0
    b1.aura_inversion_timer = 2.0 # Reversed aura

    b2 = MockBall(2, team="red") # Friendly
    b3 = MockBall(3, team="blue") # Enemy target

    world.balls = [b1, b2, b3]
    mode.timer = 0.0 # Force trigger

    mode.tick(world, world.balls, 0.016)

    # Friendly should NOT receive the reversed aura buff from the pulse
    assert b2.vampiric_aura_timer == 0.0
    assert b2.aura_inversion_timer == 0.0

    # Enemy SHOULD receive it as a debuff
    assert b3.vampiric_aura_timer == 5.0
    assert b3.aura_inversion_timer == 5.0
