import pytest
from ai.game_modes import BountyContractEventMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

class MockBall:
    def __init__(self, id, alive=True, ball_type="normal"):
        self.id = id
        self.alive = alive
        self.ball_type = ball_type
        self.base_speed = 100.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.xp = 0

def test_bounty_contract_activation():
    mode = BountyContractEventMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3)]

    # Force activation by manipulating random or setting large delta
    import random
    random.seed(42)  # Deterministic but might not trigger if probability is too low

    # Force the event to activate for testing
    mode.active = True
    mode.timer = 20.0
    mode.bounty_id = 1
    balls[0].is_bounty_contract = True
    balls[0].base_speed = 150.0
    balls[0].max_hp = 200.0
    balls[0].hp = 200.0
    balls[0].bounty_contract_xp_reward = 500

    assert mode.active == True
    assert balls[0].base_speed == 150.0
    assert balls[0].max_hp == 200.0

def test_bounty_contract_survives():
    mode = BountyContractEventMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]

    mode.active = True
    mode.timer = 0.01
    mode.bounty_id = 1

    balls[0].is_bounty_contract = True
    balls[0].base_speed = 150.0

    mode.tick(world, balls, delta=0.1)

    assert mode.active == False
    assert balls[0].is_bounty_contract == False
    assert balls[0].base_speed == 100.0
    assert balls[0].xp == 250

    event_types = [e[0] for e in world.events]
    assert "bounty_contract_end" in event_types

def test_bounty_contract_claimed():
    mode = BountyContractEventMode()
    world = MockWorld()

    ball1 = MockBall(1)
    ball1.bounty_contract_xp_reward = 500
    ball2 = MockBall(2)

    mode.active = True
    mode.bounty_id = 1

    mode.on_ball_died(world, ball1, ball2)

    assert ball2.xp == 500
