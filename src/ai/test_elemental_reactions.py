import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y, ball_type, traits=None):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.ball_type = ball_type
        self.traits = traits or []
        self.alive = True
        self.hp = 100.0
        self.burn_timer = 0.0
        self.frozen_timer = 0.0
        self.is_frozen = False
        self.stun_timer = 0.0
        self.blindness_timer = 0.0

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, evt_type, data):
        self.events.append((evt_type, data))

def test_elemental_reactions_steam_explosion():
    mode = GAME_MODES["elemental_reactions"]
    world = MockWorld()

    # Fire ball (burning) vs Water ball
    fire_ball = MockBall(0, 0, "fire")
    fire_ball.burn_timer = 5.0

    water_ball = MockBall(10, 0, "water")

    # Third ball nearby to get blinded
    bystander = MockBall(50, 0, "normal")

    balls = [fire_ball, water_ball, bystander]

    mode.tick(world, balls, 0.016)

    # The water ball hits the fire ball (which is burning)
    # This should trigger steam explosion
    assert fire_ball.burn_timer == 0.0
    assert bystander.blindness_timer >= 5.0

    explosion_event = next((e for e in world.events if e[0] == "explosion" and e[1].get("type") == "steam"), None)
    assert explosion_event is not None
    assert explosion_event[1]["radius"] == 200.0

def test_elemental_reactions_shatter():
    mode = GAME_MODES["elemental_reactions"]
    world = MockWorld()

    # Ice ball (frozen) vs Fire ball
    ice_ball = MockBall(0, 0, "ice")
    ice_ball.frozen_timer = 5.0
    ice_ball.is_frozen = True
    ice_ball.stun_timer = 5.0

    fire_ball = MockBall(10, 0, "fire")

    balls = [ice_ball, fire_ball]

    mode.tick(world, balls, 0.016)

    # The fire ball hits the ice ball (which is frozen)
    # This should trigger shatter
    assert ice_ball.frozen_timer == 0.0
    assert not ice_ball.is_frozen
    assert ice_ball.stun_timer == 0.0

    # Shatter does 50 damage
    assert ice_ball.hp == 50.0

    explosion_event = next((e for e in world.events if e[0] == "explosion" and e[1].get("type") == "shatter"), None)
    assert explosion_event is not None
    assert explosion_event[1]["damage"] == 50.0
