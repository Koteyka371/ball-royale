import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id=0, ball_type="normal", team="Blue", x=0.0, y=0.0):
        self.id = id
        self.ball_type = ball_type
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.radius = 10.0
        self.hp = 100.0

    def take_damage(self, amount, source=None):
        self.hp -= amount

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type_str, payload):
        self.events.append((type_str, payload))

def test_thermal_payload_growth():
    mode = GAME_MODES["thermal_payload"]
    world = MockWorld()

    player1 = MockBall(1, "normal", "Blue", 500.0, 500.0) # Near payload
    player2 = MockBall(2, "normal", "Red", 900.0, 900.0) # Far from payload
    balls = [player1, player2]

    mode.setup(world, balls)

    # Assert payload was added
    assert any(getattr(b, "ball_type", "") == "payload" for b in balls)

    payload = mode.payload
    initial_radius = payload.aura_radius

    # Tick with player1 pushing
    mode.tick(world, balls, 0.1)

    assert payload.pushed_this_tick == True
    assert payload.unpushed_timer == 0.0
    assert payload.aura_radius > initial_radius

    # Check that far player takes no damage, close player might take aura damage
    hp2_before = player2.hp
    mode.tick(world, balls, 0.1)
    assert player2.hp == hp2_before

def test_thermal_payload_explosion():
    mode = GAME_MODES["thermal_payload"]
    world = MockWorld()

    player = MockBall(1, "normal", "Blue", 900.0, 900.0) # Far away initially
    balls = [player]

    mode.setup(world, balls)
    payload = mode.payload

    # Manually set aura radius and unpushed_timer close to explosion
    payload.aura_radius = 200.0
    payload.unpushed_timer = 2.95

    # Move player into explosion range
    player.x = 700.0
    player.y = 500.0
    hp_before = player.hp

    # Tick to push over 3.0 timer
    mode.tick(world, balls, 0.1)

    assert payload.unpushed_timer == 0.0 # reset
    assert payload.aura_radius == 40.0 # reset
    assert player.hp < hp_before # Took explosion damage

    # Check visual effect event
    assert any(e[0] == "visual_effect" and e[1]["type"] == "massive_explosion" for e in world.events)
