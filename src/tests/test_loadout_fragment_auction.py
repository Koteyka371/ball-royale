import pytest
from ai.game_modes import GAME_MODES

class MockEntity:
    def __init__(self, e_id, fragments):
        self.id = e_id
        self.alive = True
        self.ball_type = "normal"
        self.loadout_fragments = fragments
        self.base_speed = 100.0
        self.base_damage = 10.0

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_loadout_fragment_auction_mode():
    mode = GAME_MODES.get("loadout_fragment_auction")
    assert mode is not None

    world = MockWorld()
    b1 = MockEntity(1, 10)
    b2 = MockEntity(2, 5)

    # Start auction
    mode.auction_timer = 0
    mode.tick(world, [b1, b2], delta=0.1)
    assert mode.auction_active == True

    # Simulate bidding
    mode.current_highest_bid = 8
    mode.highest_bidder = b1

    # End auction
    mode.auction_duration = 0
    mode.tick(world, [b1, b2], delta=0.1)

    assert not mode.auction_active
    assert b1.loadout_fragments == 2
    assert b1.base_speed == 150.0
    assert b1.base_damage == 35.0

    won_events = [e for e in world.events if e[0] == "fragment_auction_won"]
    assert len(won_events) == 1
    assert won_events[0][1]["winner_id"] == 1
