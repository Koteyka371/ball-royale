import pytest
from ai.game_modes import GAME_MODES, BlindAuctionEventMode

class MockEntity:
    def __init__(self, id, alive=True, ball_type="player", loadout_fragments=10, max_hp=100.0, hp=100.0, base_speed=100.0, base_damage=10.0):
        self.id = id
        self.alive = alive
        self.ball_type = ball_type
        self.loadout_fragments = loadout_fragments
        self.max_hp = max_hp
        self.hp = hp
        self.base_speed = base_speed
        self.base_damage = base_damage
        self.cosmetics = []

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

def test_blind_auction_initialization():
    mode = GAME_MODES["blind_auction_event"]
    assert isinstance(mode, BlindAuctionEventMode)
    assert mode.name == "Blind Auction Event"

def test_blind_auction_tick_starts_auction():
    mode = BlindAuctionEventMode()
    mode.auction_timer = 0.1
    world = MockWorld()
    balls = [MockEntity(1)]
    mode.tick(world, balls, delta=0.2)
    assert mode.auction_active is True
    assert mode.auction_duration == 5.0
    assert any(e[0] == "blind_auction_started" for e in world.events)

def test_blind_auction_tick_bidding():
    mode = BlindAuctionEventMode()
    mode.auction_active = True
    mode.auction_duration = 5.0
    world = MockWorld()
    balls = [MockEntity(1, loadout_fragments=100), MockEntity(2, loadout_fragments=50)]

    # Force bidding by giving large delta (it uses random.random() < 3.0 * delta)
    for _ in range(10):
        mode.tick(world, balls, delta=1.0)
        if mode.bids:
            break

    assert len(mode.bids) > 0
    assert any(e[0] == "blind_auction_bid_placed" for e in world.events)

def test_blind_auction_tick_resolves_auction():
    mode = BlindAuctionEventMode()
    mode.auction_active = True
    mode.auction_duration = 0.1
    mode.bids = {1: 50, 2: 30}
    mode.item_reward = {"max_hp": 100, "base_speed": 50, "base_damage": 20}
    mode.cosmetic_reward = ""

    world = MockWorld()
    b1 = MockEntity(1, loadout_fragments=100)
    b2 = MockEntity(2, loadout_fragments=100)
    balls = [b1, b2]

    mode.tick(world, balls, delta=0.2)

    assert mode.auction_active is False
    assert mode.auction_timer > 0
    assert b1.loadout_fragments == 50
    assert b1.max_hp == 200.0
    assert b1.base_speed == 150.0
    assert b1.base_damage == 30.0

    # Test cosmetic reward resolution
    mode.auction_active = True
    mode.auction_duration = 0.1
    mode.bids = {2: 40}
    mode.item_reward = {}
    mode.cosmetic_reward = "Golden Aura"

    mode.tick(world, balls, delta=0.2)

    assert mode.auction_active is False
    assert b2.loadout_fragments == 60
    assert "Golden Aura" in b2.cosmetics
