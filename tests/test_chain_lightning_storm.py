import pytest
from ai.game_modes import ChainLightningStormMode
from arena.procedural_arena import Hazard

class MockWorld:
    def __init__(self):
        self.events = []
        self.dead_balls = []
        self.arena = self.MockArena()

    class MockArena:
        def __init__(self):
            self.hazards = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

    def _deal_damage(self, attacker, target, damage=0.0):
        target.hp -= damage


class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.ball_type = "player"
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.alive = True
        self.team = "A"


def test_chain_lightning_storm_mode():
    world = MockWorld()
    balls = [
        MockBall("b1", 100, 100),
        MockBall("b2", 150, 150),
        MockBall("b3", 500, 500)
    ]

    mode = ChainLightningStormMode()
    assert not mode.event_active

    # Fast forward until event triggers
    for _ in range(1600):
        mode.tick(world, balls, delta=0.01)
        if mode.event_active:
            break

    assert mode.event_active
    assert len(mode.strikes) > 0

    # Store initial states
    b1_start_hp = balls[0].hp

    # Move a ball to exactly where the first strike will hit
    target_strike = mode.strikes[0]
    balls[0].x = target_strike["x"]
    balls[0].y = target_strike["y"]
    balls[0].chain_lightning_timer = 0.0

    # Fast forward until warning finishes and strike hits
    time_to_strike = target_strike["timer"]

    # Tick past the warning timer
    while target_strike["state"] == "warning":
        mode.tick(world, balls, delta=0.1)
        if not mode.event_active:
            break

    # Now the strike should have hit and applied effects
    assert balls[0].hp < b1_start_hp
    assert balls[0].chain_lightning_timer > 0.0

    # Assert hazards were correctly added to the world
    has_active = any(h.kind == "chain_lightning_active" for h in world.arena.hazards)
    assert has_active

    # Ensure event ends
    for _ in range(100):
        mode.tick(world, balls, delta=0.1)

    assert not mode.event_active
