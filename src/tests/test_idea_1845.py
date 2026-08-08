import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
import sys
sys.path.append('src')
from ai.game_modes import BattleRoyaleMode, TelegraphedSupplyDropMode, EscortMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.name = "test"
        self.weather = "clear"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []
        self.mutators_active = False
        self.boosters = []
        self.tick_timer = 0.0

    def add_event(self, kind, data):
        self.events.append({"type": kind, **data})

class MockBall:
    def __init__(self, x=0.0, y=0.0, team="Neutral", radius=15.0, ball_type="normal"):
        self.x = x
        self.y = y
        self.team = team
        self.radius = radius
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.shield = 0.0
        self.ultimate_charge = 0.0
        self.max_ultimate_charge = 100.0
        self.invulnerable_timer = 0.0
        self.vx = 0.0
        self.vy = 0.0

def test_battle_royale_shockwave():
    mode = BattleRoyaleMode()
    world = MockWorld()

    # Force the timer
    mode.supply_drop_timer = 14.9

    # Target location to intercept drop
    b = MockBall(x=500.0, y=500.0)
    balls = [b]

    # Mock random to predictable location
    class PredictableRandom:
        def random(self): return 0.5
        def uniform(self, a, b):
            return 500.0
        def choice(self, lst):
            return lst[0]
        def randint(self, a, b):
            return 1

    mode.random = PredictableRandom()
    mode.tick(world, balls, delta=0.2)

    events = [e for e in world.events if e.get("type") == "supply_drop_shockwave"]
    assert len(events) >= 1, "Should emit a shockwave event"

    assert b.hp == 70.0, "Ball should take 30 damage from shockwave"

def test_telegraphed_drop_shockwave():
    mode = TelegraphedSupplyDropMode()
    world = MockWorld()

    b = MockBall(x=500.0, y=500.0)
    balls = [b]

    mode.active_telegraphs = [
        {"id": "test_t", "x": 500.0, "y": 500.0, "radius": 50.0, "timer": 0.1, "active": True}
    ]

    mode.tick(world, balls, delta=0.2)

    events = [e for e in world.events if e.get("type") == "supply_drop_shockwave"]
    assert len(events) >= 1, "Should emit a shockwave event"

    assert b.hp == 70.0, "Ball should take 30 damage from shockwave"
