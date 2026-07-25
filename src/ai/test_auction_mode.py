import pytest
from ai.game_modes import GAME_MODES

class DummyWorld:
    def __init__(self):
        self.events = []
        self.arena = None
        self.match_time = 0.0

    def add_event(self, name, data):
        self.events.append((name, data))

class DummyBall:
    def __init__(self, bid, x, y, alive=True):
        self.id = bid
        self.x = x
        self.y = y
        self.alive = alive
        self.gold = 0
        self.max_hp = 100.0
        self.hp = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.ball_type = "normal"

def test_auction_event_mode():
    mode = GAME_MODES["auction_event"]
    mode.auction_timer = 0.1 # Almost ready

    world = DummyWorld()
    ball1 = DummyBall("b1", 0, 0)
    ball1.gold = 100
    ball2 = DummyBall("b2", 10, 10)
    ball2.gold = 500

    balls = [ball1, ball2]

    # Trigger auction
    mode.tick(world, balls, 0.2)
    assert mode.auction_active == True
    assert any(e[0] == "auction_started" for e in world.events)

    # Fast forward bidding
    mode.tick(world, balls, 0.5)
    # Mocking random makes it tricky, let's just force a bid
    mode.highest_bidder = ball2
    mode.current_bid = 100

    # End auction
    mode.auction_duration = 0.1
    mode.tick(world, balls, 0.2)
    assert mode.auction_active == False
    assert ball2.gold == 500 - mode.current_bid
    assert ball2.max_hp > 100.0
    assert any(e[0] == "auction_won" for e in world.events)
