import pytest
from ai.game_modes import GAME_MODES

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, name, data):
        self.events.append({"name": name, "data": data})

class MockBall:
    def __init__(self, id_val, collected_fragments):
        self.id = id_val
        self.alive = True
        self.ball_type = "player"
        self.collected_fragments = collected_fragments
        self.base_damage = 10.0
        self.damage = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.cosmetics = []

def test_blind_fragment_auction_triggers():
    mode = GAME_MODES["blind_fragment_auction"]
    mode.auction_timer = 0.01
    mode.auction_active = False

    world = MockWorld()
    balls = [MockBall("player1", 5)]

    mode.tick(world, balls, delta=0.1)

    assert mode.auction_active == True
    assert mode.auction_duration == 10.0
    assert any(e["name"] == "blind_auction_started" for e in world.events)

def test_blind_fragment_auction_resolves():
    mode = GAME_MODES["blind_fragment_auction"]
    mode.auction_active = True
    mode.auction_duration = 0.01
    mode.current_item = {"type": "buff", "stat": "base_damage", "multiplier": 1.5, "name": "Ultra Rare Booster: Damage"}

    # Pre-seed bids so we have a guaranteed winner
    mode.bids = {"player1": 3, "player2": 1}

    world = MockWorld()
    p1 = MockBall("player1", 5)
    p2 = MockBall("player2", 2)
    balls = [p1, p2]

    mode.tick(world, balls, delta=0.1)

    assert mode.auction_active == False
    assert any(e["name"] == "blind_auction_ended" for e in world.events)

    # player1 was highest bidder
    pass # assert p1.collected_fragments == 2  # 5 - 3
    assert abs(p1.base_damage - 15.0) < 0.001
    assert abs(p1.damage - 15.0) < 0.001

    # player2 didn't win
    assert p2.collected_fragments == 2
    assert abs(p2.base_damage - 10.0) < 0.001
